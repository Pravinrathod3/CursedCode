# 01 — Architecture & Data Flow

## Logical services

1. **FastAPI API layer** — validation, routing, response shaping.
2. **Challenge service** — trusted challenge metadata and test definitions.
3. **Execution adapter** — calls an isolated code runner.
4. **Outcome classifier** — maps runner/test results to allowed outcomes.
5. **Explanation/hint workflow** — LangChain model integration orchestrated by LangGraph.
6. **Learner model service** — deterministic mistake recurrence, mastery updates, recommendations.
7. **Supabase repository layer** — database persistence.
8. **Observability** — structured logs and optional LangSmith traces.

## Submission flow

```text
Client
  -> FastAPI POST /api/submit
  -> Validate request and load challenge
  -> Restricted runner (outside API process)
  -> Outcome classifier
  -> Sanitize execution evidence
  -> Explanation workflow (optional/failure path)
  -> Persist submission + tags + learner evidence
  -> Safe response to client
```

## Hint flow

```text
Client requests next hint
  -> FastAPI POST /api/hint
  -> Verify submission and hint index
  -> Load sanitized failure summary + prior hints
  -> LangGraph hint workflow
  -> Validate output against hint policy
  -> Persist hint and return only the next hint
```

## Learner profile flow

```text
GET /api/learner/{learner_id}
  -> Read attempts and tags from Supabase
  -> Count mistake categories across distinct challenges
  -> Update or compute concept mastery from evidence
  -> Choose an eligible practice challenge
  -> Return recurring mistakes, mastery, and recommendation reason
```

## Trust boundaries

- Learner code is untrusted.
- Runner output is data and must be parsed/size-limited.
- LLM output is untrusted and must be validated.
- Hidden test definitions are trusted server-side data and must never be sent to the browser.
- Supabase service-role credentials are backend-only.
- Observability tools must not receive secrets, raw code if not needed, or hidden test values.

## Design rule

Keep core judging and learner-model logic deterministic. Use the LLM for natural-language explanations and hint phrasing, not for security enforcement or outcome classification.
