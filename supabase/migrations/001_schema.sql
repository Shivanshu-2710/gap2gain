-- Gap2Gain core schema (PostgreSQL / Supabase)

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  timezone text not null default 'Asia/Kolkata',
  plan text not null default 'free' check (plan in ('free','premium')),
  min_hourly_pay numeric,                       -- pay preference (for matching)
  prefer_remote boolean,                        -- null = no preference
  min_block_minutes int not null default 30 check (min_block_minutes >= 15),
  buffer_minutes int not null default 10 check (buffer_minutes >= 0),
  created_at timestamptz not null default now()
);

create table public.skills (
  id uuid primary key default gen_random_uuid(),
  name text not null unique
);

create table public.user_skills (
  user_id uuid not null references public.profiles(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  level smallint not null default 3 check (level between 1 and 5),
  primary key (user_id, skill_id)
);

-- weekday: 0 = Monday ... 6 = Sunday. 'unavailable' = a gap the user marked as not usable.
create table public.routine_blocks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  weekday smallint not null check (weekday between 0 and 6),
  start_time time not null,
  end_time time not null,
  block_type text not null check (block_type in ('class','work','commute','sleep','personal','unavailable')),
  check (end_time > start_time)
);
create index on public.routine_blocks (user_id, weekday);

create table public.jobs (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text not null,
  source text not null,
  external_url text,
  duration_minutes int not null check (duration_minutes > 0),
  setup_minutes int not null default 0,
  pay_amount numeric,                           -- total pay for the gig; null = not listed
  pay_verified boolean not null default false,
  remote boolean not null default true,
  status text not null default 'open' check (status in ('open','closed')),
  flagged boolean not null default false,       -- suspicious listing
  flag_reason text,
  created_at timestamptz not null default now()
);

create table public.job_skills (
  job_id uuid not null references public.jobs(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  importance smallint not null default 2 check (importance between 1 and 3), -- 3 = required
  primary key (job_id, skill_id)
);

create table public.job_matches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  job_id uuid not null references public.jobs(id) on delete cascade,
  score numeric not null,
  reasons jsonb not null default '[]',
  computed_at timestamptz not null default now(),
  unique (user_id, job_id)
);

create table public.applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  job_id uuid not null references public.jobs(id) on delete cascade,
  status text not null default 'queued'
    check (status in ('queued','submitted','interview','rejected','offer','withdrawn')),
  -- queued_in_app = only queued inside Gap2Gain; submitted_external = really sent (deferred integration)
  mode text not null default 'queued_in_app' check (mode in ('queued_in_app','submitted_external')),
  applied_at timestamptz not null default now(),
  unique (user_id, job_id)                      -- retries can never create duplicates
);

create table public.daily_usage (
  user_id uuid not null references public.profiles(id) on delete cascade,
  usage_date date not null,
  auto_apply_count int not null default 0 check (auto_apply_count >= 0),
  primary key (user_id, usage_date)
);

create table public.resumes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  original_text text not null,
  created_at timestamptz not null default now()
);

create table public.resume_versions (
  id uuid primary key default gen_random_uuid(),
  resume_id uuid not null references public.resumes(id) on delete cascade,
  job_id uuid not null references public.jobs(id) on delete cascade,
  tailored_text text not null,
  changes_summary jsonb not null default '[]',
  created_at timestamptz not null default now()
);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  application_id uuid references public.applications(id) on delete set null,
  sender text not null,
  subject text not null,
  body text not null,
  received_at timestamptz not null default now(),
  is_read boolean not null default false,
  status text not null default 'new'
);
create index on public.messages (user_id, received_at desc);

create table public.digest_preferences (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  enabled boolean not null default true,
  delivery_time time not null default '18:00',
  timezone text not null default 'Asia/Kolkata'
);

create table public.digest_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  scheduled_for timestamptz not null,
  status text not null check (status in ('previewed','queued','sent','failed')),
  sent_at timestamptz
);

create table public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  plan text not null,
  status text not null,                         -- 'demo' in MVP; real billing is deferred
  expires_at timestamptz
);

-- Auto-create profile + digest preferences when a user signs up
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, full_name) values (new.id, new.raw_user_meta_data->>'full_name');
  insert into public.digest_preferences (user_id) values (new.id);
  return new;
end $$;

create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();
