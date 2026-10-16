"""
Judge0-backed code runner.

Calls the Judge0 REST API to execute untrusted learner code in an isolated
sandbox. Normalizes Judge0 statuses into the platform's four outcomes:
passed, wrong_output, runtime_error, timeout.

Requires:
  RUNNER_BASE_URL      e.g. https://judge0-ce.p.rapidapi.com
  RUNNER_API_KEY       RapidAPI key for Judge0
  RUNNER_TIMEOUT_SECONDS per-submission polling cap
"""
import asyncio
from urllib.parse import urlparse

import httpx

from app.core.config import get_settings
from app.core.exceptions import RunnerUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Judge0 language ID for Python 3
PYTHON_LANGUAGE_ID = 71

# Judge0 submission status IDs (RapidAPI hosted tier)
STATUS_IN_QUEUE = 1
STATUS_PROCESSING = 2
STATUS_ACCEPTED = 3
STATUS_WRONG_ANSWER = 4
STATUS_TIME_LIMIT_EXCEEDED = 5
STATUS_RUNTIME_ERROR = 11  # NZEC on this tier
STATUS_COMPILATION_ERROR = 7
STATUS_INTERNAL_ERROR = 8
STATUS_EXEC_FORMAT_ERROR = 9

_JUDGE0_TO_OUTCOME = {
    STATUS_ACCEPTED: "passed",
    STATUS_WRONG_ANSWER: "wrong_output",
    STATUS_RUNTIME_ERROR: "runtime_error",
    STATUS_TIME_LIMIT_EXCEEDED: "timeout",
    STATUS_COMPILATION_ERROR: "runtime_error",
    STATUS_EXEC_FORMAT_ERROR: "runtime_error",
}


async def run_code(source_code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute source_code against each test_case via Judge0.

    Each test_case dict must contain:
        id: str
        visibility: "visible" | "hidden"
        input_payload: dict with "call" key (e.g. "last_k_total([3, 8, 2, 5], 2)")
        expected_output: any
        timeout_ms: int
    """
    settings = get_settings()
    base_url = settings.runner_base_url.rstrip("/")
    api_key = settings.runner_api_key
    timeout = settings.runner_timeout_seconds

    if not api_key:
        raise RunnerUnavailableError("Judge0 API key is not configured.")

    host = urlparse(base_url).hostname or base_url
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        results = []
        for tc in test_cases:
            call = (tc.get("input_payload") or {}).get("call", "")
            full_source = f"{source_code}\nprint({call})"
            expected = str(tc.get("expected_output", ""))

            try:
                token = await _submit(client, base_url, headers, full_source)
                result = await _poll(client, base_url, headers, token, timeout)
            except RunnerUnavailableError:
                raise
            except Exception as exc:
                logger.error("Judge0 execution failed for test %s: %s", tc.get("id"), exc)
                result = {"outcome": "runtime_error", "actual_output": None, "duration_ms": None}

            outcome = result["outcome"]
            actual_output = result.get("actual_output")
            if outcome == "passed" and actual_output is not None:
                if str(actual_output).strip() != expected:
                    outcome = "wrong_output"

            results.append({
                "test_case_id": tc["id"],
                "visibility": tc["visibility"],
                "outcome": outcome,
                "actual_output": actual_output if tc["visibility"] == "visible" else None,
                "duration_ms": result.get("duration_ms"),
            })
        return results


async def _submit(client, base_url, headers, source_code):
    """Submit code to Judge0 and return the submission token."""
    url = f"{base_url}/submissions"
    params = {"base64_encoded": "false"}
    payload = {
        "source_code": source_code,
        "language_id": PYTHON_LANGUAGE_ID,
        "stdin": "",
    }
    resp = await client.post(url, params=params, headers=headers, json=payload)
    if resp.status_code >= 400:
        logger.error("Judge0 submission rejected: %s %s", resp.status_code, resp.text[:200])
        raise RunnerUnavailableError(f"Judge0 rejected submission (HTTP {resp.status_code}).")
    data = resp.json()
    token = data.get("token")
    if not token:
        raise RunnerUnavailableError("Judge0 did not return a submission token.")
    return token


async def _poll(client, base_url, headers, token, timeout):
    """Poll Judge0 until the submission finishes, then return the normalized result."""
    url = f"{base_url}/submissions/{token}"
    params = {"base64_encoded": "false"}
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code >= 400:
            raise RunnerUnavailableError(f"Judge0 poll failed (HTTP {resp.status_code}).")
        data = resp.json()
        status = data.get("status") or {}
        status_id = status.get("id")

        if status_id in (STATUS_IN_QUEUE, STATUS_PROCESSING):
            if asyncio.get_event_loop().time() > deadline:
                return {"outcome": "timeout", "actual_output": None, "duration_ms": None}
            await asyncio.sleep(1)
            continue

        if status_id == STATUS_INTERNAL_ERROR:
            raise RunnerUnavailableError("Judge0 internal error.")

        outcome = _JUDGE0_TO_OUTCOME.get(status_id, "runtime_error")

        stdout = data.get("stdout") or ""
        duration_ms = None
        try:
            duration_ms = int(float(data.get("time") or 0) * 1000)
        except (TypeError, ValueError):
            duration_ms = None

        return {
            "outcome": outcome,
            "actual_output": stdout.strip() or None,
            "duration_ms": duration_ms,
        }
