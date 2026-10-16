# 04 — FastAPI Setup & Conventions

## Suggested dependencies

Pin compatible versions in `requirements.txt` once installed and tested. Initial package families:

- `fastapi`
- `uvicorn[standard]`
- `pydantic-settings`
- `supabase`
- `httpx`
- `langchain`
- `langgraph`
- Provider integration package appropriate to the chosen provider
- Optional `langsmith`
- `pytest`
- `pytest-asyncio`
- `respx` or another HTTP mocking library

Avoid adding every available LangChain integration. Install only the provider package you actually use.

## App conventions

- Keep route handlers thin.
- Put domain logic in services.
- Put Supabase access in repositories.
- Use Pydantic models for all public request and response bodies.
- Use dependency injection for configuration, database clients, and service clients.
- Use async HTTP calls for external APIs where supported.
- Set explicit timeouts for runner and LLM requests.
- Centralize exception-to-HTTP mapping.
- Add `/health` for basic service health; do not expose secrets or internal diagnostics.

## Suggested API response handling

- `400` — malformed request or invalid request field, where appropriate
- `404` — unknown challenge or submission
- `422` — Pydantic validation error
- `429` — rate limit exceeded
- `502`/`503` — upstream runner/provider unavailable
- `504` — upstream service timeout, when the API request itself times out

Do not return HTTP 200 with a fake “passed” result when a dependency fails.

## Development modes

Support explicit modes:
- `mock` — local development only, clearly marked
- `live` — real runner/provider configured

Never silently fall back to a mock runner in production or judging mode.

## API documentation

FastAPI's OpenAPI docs are useful for the team. Keep examples sanitized and never include real keys, hidden test values, or actual private exception messages.
