# 02 — Backend Rules & Security

## Non-negotiable rules

1. Never execute submitted code inside the FastAPI process.
2. Never run untrusted code with the application server's privileges.
3. Never expose hidden test input, expected output, actual output, raw hidden exceptions, or hidden test file paths.
4. Never send hidden test data or server secrets to the LLM.
5. Never trust model output without validation.
6. Never report a submission as passed if execution was killed, incomplete, malformed, or infrastructure-failed.
7. Never treat an API/runner outage as a learner runtime error.
8. Never put secrets in Git, frontend bundles, API responses, logs, or traces.
9. Use pseudonymous learner IDs and minimum necessary data.
10. Treat code, model output, and runner messages as untrusted input.

## Runner isolation controls

Use a dedicated isolated execution service. Apply controls appropriate to the chosen runner:
- CPU/time limit
- Memory limit
- Output-size limit
- Process-count limit where supported
- Restricted filesystem and temporary working directory
- No network access unless explicitly required (it is not required for these challenges)
- Non-root execution and dropped privileges
- Read-only base filesystem where practical
- Container/OS sandboxing with secure configuration
- Cleanup after each run
- Separate runner credentials and network boundaries from the API/database

A plain Python subprocess plus a timeout is not a complete sandbox.

## API controls

- Validate `learner_id`, `challenge_id`, code length, and content types.
- Add request timeouts and concurrency limits.
- Limit response body and runner output sizes.
- Apply rate limiting if time permits.
- Return generic errors for unexpected internal failures.
- Keep detailed internal diagnostics in restricted logs only, with sensitive fields redacted.
- Use parameterized database queries through the Supabase client or safe SQL APIs.

## Hidden-test secrecy

- Store hidden tests in trusted backend storage, not public frontend bundles.
- Send only the data required for execution to the isolated runner.
- The runner should return outcomes for hidden tests, not details.
- Do not include hidden inputs/expected values in prompt context, traces, analytics, exceptions, or client responses.
- Test secrecy with hostile submissions that print arguments, raise exceptions, inspect files, and attempt to read environment variables.

## LLM safety

- Model output is advisory, never authoritative for pass/fail.
- Use structured output where possible.
- Limit output tokens and request timeouts.
- Validate hints for full-solution leakage and unsafe content.
- Do not rely on prompt instructions alone as a security boundary.
- Have a deterministic fallback explanation if the provider is unavailable.

## Privacy

Use pseudonymous learner IDs. Avoid storing names, emails, or other real student data unless the product genuinely requires it.
