# Gap2Gain (MVP)

Turn the free gaps in a student's day into matched gig work.
**Stack:** FastAPI + Supabase (PostgreSQL, Auth, RLS) + React (Vite).

## Setup
1. **Supabase:** create a project, then in the SQL editor run, in order:
   `supabase/migrations/001_schema.sql` → `002_rls_and_functions.sql` → `supabase/seed.sql`.
2. **Backend**
   ```bash
   cd backend && python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env        # fill in Supabase URL + service-role key
   python -m scripts.create_demo_user
   uvicorn app.main:app --reload
   ```
   Tests (no database needed): `pytest`. API docs: http://localhost:8000/docs
3. **Frontend**
   ```bash
   cd frontend && cp .env.example .env   # fill in URL + anon key
   npm install && npm run dev
   ```
   Click **Try demo**.

## Demo script for judges
Schedule → see free blocks · Find Work → ranked matches with reasons, a flagged listing, 5 free
queued applications (6th is refused by the database) · Resume Studio → premium gate → simulated
upgrade → side-by-side tailored resume · Applications & Inbox → sample replies + digest preview.

## Scope
Built: demo login, routine/availability, seeded jobs + transparent matching, application queue,
atomic daily quota, fact-checked resume tailoring, sample inbox + digest preview, premium gating.
Deferred: external auto-submission, real inbox sync, billing, scraping, background queues.
The UI always says "queued in Gap2Gain", never "submitted".

## Security notes
- Service-role key lives only in `backend/.env`; the frontend only gets the anon key.
- The API uses the service role (bypasses RLS) so **every query must filter by `user_id`**. RLS has
  select-only policies as defence in depth; there are no client write policies (users can't self-upgrade).
- Quota = Postgres function `reserve_auto_apply` (atomic, idempotent per user+job).
- Resumes/job text are treated as untrusted; AI output is validated (no new numbers) and needs user review.

## Folder structure
See the tree in the chat reply or run `tree -I node_modules`.
