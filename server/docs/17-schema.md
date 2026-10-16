-- DEBUG DOJO DATABASE SCHEMA — PART 1 OF 2
-- Run this file FIRST in Supabase SQL Editor.
-- Creates the core challenge catalog, concepts, and test cases.
-- IMPORTANT: test_cases contains hidden inputs/expected outputs. Never expose it to the frontend.

begin;

create extension if not exists pgcrypto;

do $$ begin
  create type public.challenge_difficulty as enum ('beginner', 'intermediate', 'advanced');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.test_visibility as enum ('visible', 'hidden');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.test_outcome as enum ('passed', 'wrong_output', 'runtime_error', 'timeout');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.submission_status as enum ('queued', 'running', 'completed', 'infrastructure_error');
exception when duplicate_object then null; end $$;

create table if not exists public.learners (
  id uuid primary key default gen_random_uuid(),
  learner_key text not null unique default ('lrn_' || encode(gen_random_bytes(12), 'hex')),
  display_name text,
  created_at timestamptz not null default now(),
  last_active_at timestamptz
);

create table if not exists public.concepts (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  description text not null default ''
);

create table if not exists public.challenges (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  statement text not null,
  function_signature text not null,
  starter_code text not null,
  difficulty public.challenge_difficulty not null,
  language text not null default 'python' check (language = 'python'),
  is_published boolean not null default false,
  sort_order integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists challenges_published_order_idx
  on public.challenges (is_published, sort_order, difficulty);

create table if not exists public.challenge_concepts (
  challenge_id uuid not null references public.challenges(id) on delete cascade,
  concept_id uuid not null references public.concepts(id) on delete restrict,
  is_primary boolean not null default false,
  primary key (challenge_id, concept_id)
);

create table if not exists public.test_cases (
  id uuid primary key default gen_random_uuid(),
  challenge_id uuid not null references public.challenges(id) on delete cascade,
  visibility public.test_visibility not null,
  ordinal integer not null check (ordinal > 0),
  input_payload jsonb not null,
  expected_output jsonb not null,
  -- Optional learner-safe description; do not put hidden test values here.
  description text,
  timeout_ms integer not null default 1500 check (timeout_ms between 100 and 10000),
  unique (challenge_id, visibility, ordinal)
);

create index if not exists test_cases_challenge_idx
  on public.test_cases (challenge_id, visibility, ordinal);

-- Required mistake taxonomy for the hackathon.
create table if not exists public.mistake_categories (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  description text not null,
  detection_guidance text not null default ''
);

insert into public.mistake_categories (slug, name, description, detection_guidance)
values
  ('off_by_one', 'Off-by-one error', 'Loop or index range is one position too short or too long.',
   'Inspect loop bounds and first/last included index; check boundary cases.'),
  ('unhandled_short_input', 'Unhandled short input', 'Empty or too-short input is not handled correctly.',
   'Check empty input and input lengths below the expected minimum.'),
  ('print_not_return', 'Print instead of return', 'The function prints instead of returning the required value.',
   'Compare captured stdout with the required return value.'),
  ('boundary_comparison', 'Boundary comparison', 'A strict comparison is used where an inclusive comparison is required, or vice versa.',
   'Test values exactly on the boundary.'),
  ('mutates_input', 'Mutates input', 'The function changes an input collection when it should preserve it.',
   'Compare input snapshots before and after execution.')
on conflict (slug) do nothing;

-- Seed useful concepts. Add more as needed.
insert into public.concepts (slug, name, description)
values
  ('loops', 'Loops', 'Iteration and loop boundaries'),
  ('lists', 'Lists', 'Indexing, slicing, and collection behavior'),
  ('conditionals', 'Conditionals', 'Boolean conditions and boundary comparisons'),
  ('functions', 'Functions', 'Parameters, return values, and function contracts'),
  ('edge-cases', 'Edge cases', 'Empty, short, and boundary inputs')
on conflict (slug) do nothing;

-- Enable RLS. No direct client policies are created; access through FastAPI.
alter table public.learners enable row level security;
alter table public.concepts enable row level security;
alter table public.challenges enable row level security;
alter table public.challenge_concepts enable row level security;
alter table public.test_cases enable row level security;
alter table public.mistake_categories enable row level security;

commit;

-- DEBUG DOJO DATABASE SCHEMA — PART 2 OF 2
-- Run this file SECOND, after part 1.
-- Adds submissions, per-test results, mistake tracking, hints, and concept mastery.
-- Keep hidden test data and all database credentials server-side.

begin;

create table if not exists public.submissions (
  id uuid primary key default gen_random_uuid(),
  public_id text not null unique default ('sub_' || encode(gen_random_bytes(12), 'hex')),
  learner_id uuid not null references public.learners(id) on delete cascade,
  challenge_id uuid not null references public.challenges(id) on delete restrict,
  source_code text not null,
  status public.submission_status not null default 'queued',
  visible_passed integer not null default 0 check (visible_passed >= 0),
  visible_total integer not null default 0 check (visible_total >= 0),
  hidden_passed integer not null default 0 check (hidden_passed >= 0),
  hidden_total integer not null default 0 check (hidden_total >= 0),
  overall_passed boolean not null default false,
  hints_requested integer not null default 0 check (hints_requested >= 0),
  execution_ms integer check (execution_ms is null or execution_ms >= 0),
  resource_limit_hit text check (
    resource_limit_hit is null or resource_limit_hit in ('memory', 'output', 'disk', 'processes', 'time')
  ),
  explanation text,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  check (visible_passed <= visible_total),
  check (hidden_passed <= hidden_total)
);

create index if not exists submissions_learner_recent_idx
  on public.submissions (learner_id, created_at desc);

create index if not exists submissions_challenge_recent_idx
  on public.submissions (challenge_id, created_at desc);

create table if not exists public.test_results (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(id) on delete cascade,
  test_case_id uuid not null references public.test_cases(id) on delete restrict,
  outcome public.test_outcome not null,
  -- Store actual output only for visible tests. For hidden tests, keep this NULL.
  actual_output jsonb,
  safe_message text,
  duration_ms integer check (duration_ms is null or duration_ms >= 0),
  resource_limit_hit text check (
    resource_limit_hit is null or resource_limit_hit in ('memory', 'output', 'disk', 'processes', 'time')
  ),
  created_at timestamptz not null default now(),
  unique (submission_id, test_case_id)
);

create index if not exists test_results_submission_idx
  on public.test_results (submission_id);

create table if not exists public.submission_mistakes (
  submission_id uuid not null references public.submissions(id) on delete cascade,
  mistake_category_id uuid not null references public.mistake_categories(id) on delete restrict,
  confidence numeric(4,3) check (confidence is null or confidence between 0 and 1),
  evidence_summary text not null default '',
  detected_by text not null default 'rules' check (detected_by in ('rules', 'llm', 'human')),
  created_at timestamptz not null default now(),
  primary key (submission_id, mistake_category_id)
);

create index if not exists submission_mistakes_category_idx
  on public.submission_mistakes (mistake_category_id, submission_id);

-- Curated hint ladder: at least three hints for each challenge/failure type.
create table if not exists public.challenge_hints (
  id uuid primary key default gen_random_uuid(),
  challenge_id uuid not null references public.challenges(id) on delete cascade,
  mistake_category_id uuid references public.mistake_categories(id) on delete cascade,
  hint_level integer not null check (hint_level between 1 and 5),
  hint_text text not null,
  is_active boolean not null default true,
  unique (challenge_id, mistake_category_id, hint_level)
);

create table if not exists public.concept_mastery (
  learner_id uuid not null references public.learners(id) on delete cascade,
  concept_id uuid not null references public.concepts(id) on delete cascade,
  mastery_score numeric(5,2) not null default 0 check (mastery_score between 0 and 100),
  attempts integer not null default 0 check (attempts >= 0),
  successful_attempts integer not null default 0 check (successful_attempts >= 0),
  independent_successes integer not null default 0 check (independent_successes >= 0),
  last_assessed_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (learner_id, concept_id),
  check (successful_attempts <= attempts),
  check (independent_successes <= successful_attempts)
);

create index if not exists concept_mastery_learner_idx
  on public.concept_mastery (learner_id, mastery_score asc);

  -- Minimal updated_at trigger for mastery rows.
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists concept_mastery_set_updated_at on public.concept_mastery;
create trigger concept_mastery_set_updated_at
before update on public.concept_mastery
for each row execute function public.set_updated_at();

-- Enable RLS on the remaining tables. No direct client policies are created.
alter table public.submissions enable row level security;
alter table public.test_results enable row level security;
alter table public.submission_mistakes enable row level security;
alter table public.challenge_hints enable row level security;
alter table public.concept_mastery enable row level security;

commit;