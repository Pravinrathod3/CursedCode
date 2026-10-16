"""
LLM client adapter.

Supports OpenRouter (default) or xAI Grok.  Switch providers via LLM_PROVIDER env var.
"""
import httpx
from app.core.config import get_settings
from app.core.exceptions import LLMUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
XAI_BASE = "https://api.x.ai/v1"


async def chat_completion(messages: list[dict], max_tokens: int = 512) -> str:
    """Send a chat completion request and return the assistant message text."""
    settings = get_settings()

    if settings.llm_provider == "openrouter":
        url = f"{OPENROUTER_BASE}/chat/completions"
        api_key = settings.openrouter_api_key
        model = settings.openrouter_model
    else:
        url = f"{XAI_BASE}/chat/completions"
        api_key = settings.xai_api_key
        model = settings.xai_model

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.TimeoutException as exc:
        logger.error("LLM request timed out: %s", exc)
        raise LLMUnavailableError("LLM request timed out.")
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        raise LLMUnavailableError("LLM provider returned an error.")
