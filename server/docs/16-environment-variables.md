# 16 — Environment Variables

Create `.env.example` with variable names and safe placeholders. Never commit actual secrets.

```dotenv
APP_ENV=development
APP_NAME=Debug Dojo API
API_PREFIX=/api
FRONTEND_ORIGIN=http://localhost:5173

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=replace_me

LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=replace_me
OPENROUTER_MODEL=replace_with_current_model_id

# If using xAI instead of OpenRouter:
XAI_API_KEY=replace_me
XAI_MODEL=replace_with_current_model_id

RUNNER_BASE_URL=http://localhost:2358
RUNNER_API_KEY=replace_me_if_required
RUNNER_TIMEOUT_SECONDS=5
MAX_CODE_BYTES=20000

LANGSMITH_TRACING=false
LANGSMITH_API_KEY=replace_me_if_enabled
LANGSMITH_PROJECT=debug-dojo
```

## Rules

- Set only the provider variables actually needed.
- Verify current model IDs and free-tier/rate-limit status when implementing.
- Do not prefix secrets with `VITE_`; that prefix is for frontend-exposed Vite variables.
- `SUPABASE_SERVICE_ROLE_KEY` is privileged. Keep it server-side and do not expose it to the frontend.
- Keep `.env` ignored by Git.
- Validate required variables at application startup.
- Do not log the values of secrets.
- Never enable tracing with raw hidden-test data in the trace payload.
- `RUNNER_BASE_URL` must point to an appropriately isolated runner, not an unrestricted local shell wrapper.
