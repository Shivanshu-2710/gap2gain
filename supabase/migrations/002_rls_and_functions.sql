-- Row Level Security: defence in depth. The API uses the service role (bypasses RLS)
-- and filters by user_id itself; these policies protect against direct client access.
-- There are deliberately NO insert/update policies: all writes go through the API
-- (otherwise a user could set their own plan to 'premium' from the browser).

alter table public.profiles enable row level security;
create policy profiles_select_own on public.profiles for select using (auth.uid() = id);

do $$
declare t text;
begin
  foreach t in array array['user_skills','routine_blocks','job_matches','applications',
    'daily_usage','resumes','messages','digest_preferences','digest_logs','subscriptions']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy %I on public.%I for select using (auth.uid() = user_id)', t || '_select_own', t);
  end loop;
end $$;

alter table public.resume_versions enable row level security;
create policy resume_versions_select_own on public.resume_versions for select
  using (resume_id in (select id from public.resumes where user_id = auth.uid()));

-- Shared catalogues: readable by signed-in users
do $$
declare t text;
begin
  foreach t in array array['skills','jobs','job_skills']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy %I on public.%I for select to authenticated using (true)', t || '_read', t);
  end loop;
end $$;

-- Atomic quota reservation + application creation (single transaction).
-- p_limit = null means unlimited (premium).
create or replace function public.reserve_auto_apply(
  p_user uuid, p_job uuid, p_timezone text, p_limit int
) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  v_date date := (now() at time zone p_timezone)::date;
  v_app uuid;
  v_count int;
begin
  perform 1 from jobs where id = p_job and status = 'open';
  if not found then
    return jsonb_build_object('status', 'job_unavailable');
  end if;

  -- Idempotent: an existing application never consumes quota again
  select id into v_app from applications where user_id = p_user and job_id = p_job;
  if found then
    return jsonb_build_object('status', 'already_applied', 'application_id', v_app);
  end if;

  insert into daily_usage (user_id, usage_date) values (p_user, v_date) on conflict do nothing;

  -- The WHERE clause makes the check-and-increment atomic: concurrent requests
  -- serialise on the row lock, so the limit can never be exceeded.
  update daily_usage
     set auto_apply_count = auto_apply_count + 1
   where user_id = p_user and usage_date = v_date
     and auto_apply_count < coalesce(p_limit, 2147483647)
  returning auto_apply_count into v_count;

  if not found then
    return jsonb_build_object('status', 'limit_reached', 'used', p_limit);
  end if;

  begin
    insert into applications (user_id, job_id) values (p_user, p_job) returning id into v_app;
  exception when unique_violation then
    -- a concurrent duplicate won the race: give the reserved action back
    update daily_usage set auto_apply_count = auto_apply_count - 1
     where user_id = p_user and usage_date = v_date;
    select id into v_app from applications where user_id = p_user and job_id = p_job;
    return jsonb_build_object('status', 'already_applied', 'application_id', v_app);
  end;

  return jsonb_build_object('status', 'queued', 'application_id', v_app, 'used', v_count);
end $$;

-- Replace a user's whole routine atomically
create or replace function public.replace_routine(p_user uuid, p_blocks jsonb) returns void
language plpgsql security definer set search_path = public as $$
begin
  delete from routine_blocks where user_id = p_user;
  insert into routine_blocks (user_id, weekday, start_time, end_time, block_type)
  select p_user, x.weekday, x.start_time, x.end_time, x.block_type
    from jsonb_to_recordset(p_blocks) as x(weekday smallint, start_time time, end_time time, block_type text);
end $$;

revoke execute on function public.reserve_auto_apply(uuid, uuid, text, int) from public, anon, authenticated;
revoke execute on function public.replace_routine(uuid, jsonb) from public, anon, authenticated;
grant execute on function public.reserve_auto_apply(uuid, uuid, text, int) to service_role;
grant execute on function public.replace_routine(uuid, jsonb) to service_role;
