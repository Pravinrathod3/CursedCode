# Debug Dojo — Backend

Backend documentation for **Debug Dojo**, an AI-powered coding coach that helps beginners understand and fix bugs without being handed complete solutions.

## Stack

- **Python** — backend language
- **FastAPI** — REST API and request validation
- **LangChain** — LLM integration and prompt/model utilities
- **LangGraph** — stateful orchestration for the explanation/hint workflow
- **LangSmith** — optional tracing and observability for LangChain/LangGraph workflows; LangGraph itself is orchestration, not the observability product
- **OpenRouter or xAI Grok API** — LLM provider; choose one provider behind a small adapter
- **Supabase** — hosted PostgreSQL database; use server-side credentials only in the backend
- **Restricted code runner** — isolated execution service for untrusted submissions; never execute learner code inside the FastAPI process
- **Pydantic** — request/response schemas
- **pytest + httpx** — tests

## Core principles

1. The judge determines execution outcomes. The LLM explains evidence; it does not invent outcomes.
2. Never execute learner code directly in the API process or an unrestricted shell.
3. Hidden test inputs, expected outputs, actual outputs, raw exceptions, and test files stay on the trusted side.
4. Hints must become more specific without revealing a complete solution.
5. A mistake is recurring only after it appears on at least two different challenges.
6. Learner mastery is an estimate based on evidence, not a claim of certainty.
7. Use pseudonymous learner IDs; do not collect real student personal data for the hackathon.
8. Validate all model output before storing or returning it.

## Setup

Use Python 3.11+ (or the version agreed by the team).

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create `.env` from `.env.example`. Never commit `.env`.

## Provider choice: OpenRouter vs Grok

Implement a provider adapter so the application can switch without rewriting agent logic.

- **OpenRouter** can expose multiple model choices, including models that may have free tiers. Free availability, rate limits, and model names can change; verify them when building and keep a deterministic fallback for non-AI core functionality.
- **xAI Grok** is another option if the team has an API key and access to a suitable model. Do not assume API usage is free.
- Do not put provider API keys in frontend variables or source control.
- The backend must handle timeouts, rate limits, invalid model output, and provider outages.

For a 24-hour hackathon, choose one provider first. Avoid spending time supporting multiple providers before the core flow works.

## Documentation map

- [`docs/00-overview.md`](docs/00-overview.md) — product scope and backend responsibilities
- [`docs/01-architecture.md`](docs/01-architecture.md) — service boundaries and request flow
- [`docs/02-rules-security.md`](docs/02-rules-security.md) — security and non-negotiable rules
- [`docs/03-stages-roadmap.md`](docs/03-stages-roadmap.md) — staged 24-hour plan
- [`docs/04-fastapi-setup.md`](docs/04-fastapi-setup.md) — application setup and configuration
- [`docs/05-api-contracts.md`](docs/05-api-contracts.md) — required endpoints and response schemas
- [`docs/06-code-execution.md`](docs/06-code-execution.md) — restricted runner design
- [`docs/07-test-harness.md`](docs/07-test-harness.md) — visible/hidden tests and outcome classification
- [`docs/08-ai-agent-workflow.md`](docs/08-ai-agent-workflow.md) — LangChain/LangGraph workflow
- [`docs/09-hints-and-guardrails.md`](docs/09-hints-and-guardrails.md) — progressive hint policy
- [`docs/10-mistake-taxonomy.md`](docs/10-mistake-taxonomy.md) — error categories and detection
- [`docs/11-learner-model.md`](docs/11-learner-model.md) — mastery and recommendations
- [`docs/12-supabase-schema.md`](docs/12-supabase-schema.md) — tables and relationships
- [`docs/13-project-tree.md`](docs/13-project-tree.md) — suggested backend structure
- [`docs/14-observability-testing.md`](docs/14-observability-testing.md) — logs, traces, test strategy
- [`docs/15-deployment-operations.md`](docs/15-deployment-operations.md) — deployment and operations
- [`docs/16-environment-variables.md`](docs/16-environment-variables.md) — configuration reference
- [`docs/17-schema.md`](docs/17-schema.md) — database schema reference

## Required endpoints

- `POST /api/submit`
- `POST /api/hint`
- `GET /api/learner/{learner_id}`

Add health and challenge-list endpoints as needed, but preserve the required judge contract.

## Local development note

The app can start with a mock runner and mock LLM during early development, but mocks must be clearly marked. Before judging, connect the real runner and validate security boundaries. A mock must never be presented as proof of sandbox isolation.

## Definition of done

- Required API endpoints are reachable by the judges.
- Four outcomes are classified correctly: passed, wrong output, runtime error, timeout.
- Hidden tests are never exposed in responses, logs, traces, prompts, or errors.
- Untrusted code executes in a restricted environment outside the FastAPI process.
- At least three progressive hints are available per failure without providing a complete solution.
- Recurring mistakes are detected across distinct challenges.
- Learner mastery and next-challenge reasoning are returned.
- README documents a single startup command and required environment variables.
