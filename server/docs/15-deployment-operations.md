# 15 — Deployment & Operations

## Components to deploy

- FastAPI service
- Restricted execution runner (separate service or isolated deployment)
- Supabase project
- LLM provider API access
- Optional LangSmith tracing

Do not deploy an unrestricted runner in the same trust boundary as the API and database.

## Environment configuration

- Use deployment secret management for provider keys and Supabase credentials.
- Set explicit CORS origins to the frontend URL.
- Use HTTPS for public endpoints.
- Configure timeouts for runner and LLM calls.
- Configure concurrency and rate limits.
- Restrict runner network egress.
- Keep hidden test data out of static assets and public endpoints.
- Add a health endpoint without exposing internal configuration.

## Operational failure behavior

- LLM provider down: use deterministic fallback explanation/hint or return a retryable error; never fabricate a test outcome.
- Runner down: return an upstream service error; do not label the submission as a learner runtime error.
- Supabase down: return a safe error and avoid claiming progress was saved.
- LangSmith down: application should continue unless tracing is intentionally required; do not block judging on optional observability.
- Timeout: distinguish the learner execution timeout from API/provider/runner network timeout.

## Pre-judge checklist

- [ ] Required API endpoints reachable from judge environment
- [ ] Runner restrictions tested
- [ ] No secret in repository or frontend bundle
- [ ] Hidden test secrecy verified
- [ ] Four outcome labels verified
- [ ] Hint leakage tests pass
- [ ] Supabase tables and seed data ready
- [ ] CORS configured
- [ ] API docs available or contract shared
- [ ] Logs/traces redact sensitive data
- [ ] A normal submission succeeds after a hostile submission
