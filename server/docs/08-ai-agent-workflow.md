# 08 — AI Agent Workflow: LangChain + LangGraph

## Responsibilities

- **LangChain**: model/provider integration, prompt templates, structured output helpers, and related LLM utilities.
- **LangGraph**: stateful workflow orchestration, conditional edges, retries/fallback paths, and workflow state.
- **LangSmith**: optional tracing/observability for LangChain/LangGraph runs. LangGraph is not itself the observability product.

## Keep the agent narrow

Do not build a general autonomous agent with arbitrary tools. Debug Dojo needs a bounded workflow:
1. Accept sanitized failure evidence.
2. Determine the explanation category from trusted classifier output.
3. Generate a plain-language explanation or next hint.
4. Validate the generated text.
5. Persist and return only the approved output.

The LLM does not run code, decide test outcomes, access Supabase directly, or inspect hidden tests.

## Suggested graph

```text
START
  -> validate_input
  -> build_safe_context
  -> generate_explanation_or_hint
  -> validate_output
      -> approved: persist_result -> END
      -> rejected: retry_once_or_fallback -> END
```

## State fields

Use a typed state containing only what the workflow needs:
- `submission_id`
- `challenge_id`
- `failure_summary`
- `allowed_concept_tags`
- `prior_hints`
- `requested_hint_index`
- `generated_text`
- `validation_status`
- `fallback_text`

Do not include hidden test inputs, hidden expected/actual outputs, secrets, or full runner traces.

## Provider abstraction

Implement one small interface so the provider can be swapped:
- OpenRouter via its supported API/compatible client, or
- xAI Grok via its supported API/client.

Choose one provider for the hackathon. Verify current model IDs, free-tier availability, rate limits, and terms at implementation time. Do not hard-code a model name throughout the codebase.

## Reliability

- Set request timeout and output token limit.
- Handle rate limits and provider outages.
- Validate structured output.
- Keep a deterministic fallback explanation for common failures.
- Never mark a submission passed based on an LLM response.
- Do not use unrestricted agent tools.

## Prompt design

Prompts should instruct the model to:
- Explain only the supplied safe evidence.
- Avoid complete corrected functions.
- Return one hint at the requested level.
- Avoid guessing when evidence is insufficient.
- Avoid exposing internal implementation details.

Prompt instructions are not sufficient by themselves; output validation and adversarial tests are still required.
