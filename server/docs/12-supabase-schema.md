# 12 — Supabase Database Schema

Use Supabase PostgreSQL for persistence. Keep the service-role key on the backend only. Enable Row Level Security when tables are exposed through Supabase APIs; if the FastAPI service accesses data with a service-role credential, enforce application-level authorization because that key bypasses RLS.

## Suggested tables

### `challenges`

- `id` text primary key
- `title` text
- `statement` text
- `difficulty` text
- `language` text
- `function_signature` text
- `starter_code` text
- `concept_tags` jsonb or a normalized relation
- `visible_tests` jsonb
- `hidden_tests` jsonb — trusted backend only; never expose through public challenge queries
- `created_at` timestamptz

For stronger separation, store hidden tests in a separate private table/schema with stricter access controls rather than the same publicly queryable table.

### `submissions`

- `id` uuid primary key
- `learner_id` text
- `challenge_id` text references challenges
- `source_code` text (retention policy should be considered)
- `status` text
- `visible_results` jsonb
- `hidden_summary` jsonb — outcomes only
- `mistake_tags` jsonb
- `explanation` text
- `hints_used` integer default 0
- `created_at` timestamptz

Do not persist hidden inputs/expected/actual outputs in `hidden_summary`.

### `hint_events`

- `id` uuid primary key
- `submission_id` uuid references submissions
- `hint_index` integer
- `hint_text` text
- `created_at` timestamptz
- unique constraint on `(submission_id, hint_index)`

### `mistake_events`

- `id` uuid primary key
- `learner_id` text
- `submission_id` uuid references submissions
- `challenge_id` text
- `category` text
- `evidence_summary` text
- `created_at` timestamptz

### `learner_concept_mastery`

- `learner_id` text
- `concept` text
- `estimate` numeric
- `evidence_count` integer
- `updated_at` timestamptz
- composite primary key `(learner_id, concept)`

## Indexes

Consider indexes on:
- `submissions(learner_id, created_at)`
- `submissions(challenge_id)`
- `mistake_events(learner_id, category, challenge_id)`
- `hint_events(submission_id, hint_index)`

## Data rules

- Use pseudonymous learner IDs.
- Do not require real names/emails for the demo.
- Keep hidden test data out of public challenge-list responses.
- Limit source-code retention to what the learning workflow needs.
- Use parameterized queries or the official client.
- Never commit Supabase service-role keys.
- Store secrets in deployment environment variables.
