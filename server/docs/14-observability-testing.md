# 14 — Observability & Testing

## Terminology

- **LangGraph** orchestrates the workflow.
- **LangSmith** can trace and inspect LangChain/LangGraph runs, if enabled.
- Structured application logs and metrics are still required; tracing does not replace them.

## What to log

Use structured logs with:
- request/correlation ID
- endpoint
- pseudonymous learner ID (or a non-reversible internal identifier where practical)
- challenge ID
- submission ID
- runner status
- normalized outcome counts
- LLM provider/model label (not API key)
- latency and retry count
- error category

## Never log

- Provider API keys
- Supabase service-role key
- Hidden test inputs or expected outputs
- Raw hidden-test exceptions
- Environment variables
- Unnecessary full learner code
- Sensitive user data

Be careful with LangSmith payload tracing: traces may include prompts and model inputs by default depending on configuration. Sanitize data before tracing, disable tracing where safe redaction is not possible, and never include hidden test details in the workflow state.

## Test layers

### Unit tests
- Outcome mapping
- Recurrence requires distinct challenge IDs
- Hint index progression
- Mastery update function
- Safe response shaping

### API tests
- Required request/response schemas
- Unknown challenge/submission
- Invalid code payload
- Provider/runner unavailable
- Supabase error

### Integration tests
- Real runner with known programs
- Supabase persistence
- LLM provider success and failure
- Hint workflow end-to-end

### Security tests
- Infinite loop
- Memory/output flood
- File read attempt
- Network attempt
- Environment variable read attempt
- Hidden test output/exception attempts
- Hint leakage, including merged hints
- Oversized/malformed requests

## Demo evidence

Keep a small script or Postman collection that demonstrates:
1. A passing submission
2. Wrong output
3. Runtime error
4. Timeout
5. Safe hidden-test summary
6. Three progressive hints
7. Recurring mistake across two different challenges
8. Next challenge reason

## Observability budget

For a short hackathon, prioritize structured logs and a request ID first. Add LangSmith only after verifying privacy settings and avoiding sensitive payloads.
