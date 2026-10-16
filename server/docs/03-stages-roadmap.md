# 03 — Backend Stages & 24-Hour Roadmap

## Stage 0 — Contracts and skeleton (Hour 0–2)

- Create FastAPI app, health endpoint, configuration, and logging.
- Define Pydantic request/response models.
- Agree API contract with frontend.
- Add `.env.example` and startup instructions.

**Acceptance:** API starts; `/docs` and health endpoint work; secrets are not committed.

## Stage 1 — Challenge data and database (Hour 2–4)

- Create challenge metadata and test schemas.
- Set up Supabase tables.
- Seed the four judge challenges.
- Keep hidden tests server-side only.

**Acceptance:** API can load a challenge and distinguish visible from hidden tests.

## Stage 2 — Runner integration (Hour 4–8)

- Connect to a restricted execution service.
- Enforce timeout and resource constraints.
- Normalize runner output.
- Implement the four outcome labels.

**Acceptance:** pass, wrong output, runtime error, timeout tests behave correctly.

## Stage 3 — Submit API (Hour 8–10)

- Implement `POST /api/submit`.
- Return visible test details and safe hidden summaries.
- Persist submission metadata.
- Add request validation and error handling.

**Acceptance:** submission response matches frontend contract and leaks no hidden data.

## Stage 4 — Explanation/hint agent (Hour 10–14)

- Configure one LLM provider.
- Build LangGraph state flow and LangChain model adapter.
- Generate explanations from sanitized evidence.
- Add progressive hints and validation.

**Acceptance:** hints are ordered, useful, and do not contain full solutions.

## Stage 5 — Learner model (Hour 14–17)

- Implement mistake taxonomy.
- Count categories across distinct challenge IDs.
- Compute a simple mastery estimate.
- Recommend targeted practice with a reason.

**Acceptance:** repeated mistakes and next-challenge rationale work with seeded test data.

## Stage 6 — API integration and observability (Hour 17–19)

- Verify all required endpoint shapes.
- Add structured logs and correlation IDs.
- Add LangSmith tracing only with sensitive data filtered.
- Test provider outage and runner outage behavior.

**Acceptance:** traces help debug workflows without storing hidden tests or secrets.

## Stage 7 — Red-team and regression testing (Hour 19–22)

- Test infinite loops, large output, memory pressure, filesystem access, network attempts, and malformed submissions.
- Test hint leakage and hidden-test secrecy.
- Test database failures and LLM rate limits.

**Acceptance:** hostile code is contained; normal submissions still work afterward.

## Stage 8 — Freeze and viva (Hour 22–24)

- Deploy API and runner.
- Confirm judge access to required endpoints.
- Prepare README and one-command startup.
- Practise explaining isolation, test harness, hint guardrails, and learner model.

## Priority if behind schedule

1. Secure runner + correct outcome labels
2. Required APIs + hidden-test secrecy
3. Three progressive hints
4. Recurring mistakes + learner recommendation
5. Tracing and optional refinements

Do not sacrifice isolation or hidden-test secrecy to add more AI features.
