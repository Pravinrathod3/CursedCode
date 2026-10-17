"""
Code execution runner client via Judge0 REST API.
Executes learner code in Judge0's isolated sandbox.
If Judge0 is unreachable, fails closed with RunnerUnavailableError rather
than executing learner code outside a sandbox.
Guarantees hidden test inputs, outputs, and runner internals stay strictly
server-side. Classifies outcomes into exactly four states: passed,
wrong_output, runtime_error, timeout.
Also detects when learner code mutates its input lists (mutates_input).
"""
import ast
import asyncio
import json
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


def _build_mutated_source(source_code: str, call_str: str) -> str:
    """
    Build source code that executes the call and checks if any list argument
    was mutated. Uses variable assignments so we can compare before/after.
    Returns the full source string to send to Judge0.
    """
    # Parse call: func(arg1, arg2, ...)
    try:
        tree = ast.parse(f"_tmp = {call_str}", mode="exec")
        assign = tree.body[0]
        if not isinstance(assign.value, ast.Call):
            return f"{source_code}\nprint({call_str})"
        call_node = assign.value
    except Exception:
        return f"{source_code}\nprint({call_str})"

    func_name = call_node.func.id if isinstance(call_node.func, ast.Name) else "func"

    preamble = [source_code, "import json"]
    arg_assignments = []
    call_vars = []
    list_info = []  # (var_name, original_source) for list args

    for i, arg in enumerate(call_node.args):
        if isinstance(arg, ast.List):
            var_name = f"_mut_list_{i}"
            list_source = ast.unparse(arg)
            arg_assignments.append(f"{var_name} = {list_source}")
            call_vars.append(var_name)
            list_info.append((var_name, list_source))
        else:
            var_name = f"_mut_arg_{i}"
            arg_source = ast.unparse(arg)
            arg_assignments.append(f"{var_name} = {arg_source}")
            call_vars.append(var_name)

    preamble.extend(arg_assignments)

    # Call function with variables
    call_with_vars = f"{func_name}({', '.join(call_vars)})"
    preamble.append(f"_result = {call_with_vars}")

    # Mutation checks for each list argument
    for var_name, list_source in list_info:
        preamble.append(f"if {var_name} != {list_source}:")
        preamble.append('    print("___MUTATED_INPUT___")')

    preamble.append('try:')
    preamble.append('    _dumped = json.dumps(_result)')
    preamble.append('except Exception:')
    preamble.append('    _dumped = json.dumps(repr(_result))')
    preamble.append('print("___RESULT___" + _dumped)')

    return "\n".join(preamble)


def _parse_mutated_output(stdout: str) -> tuple:
    """Parse Judge0 stdout to extract (actual_output, mutated_flag)."""
    actual = None
    mutated = False
    for line in (stdout or "").splitlines():
        if line.startswith("___RESULT___"):
            payload = line[len("___RESULT___"):]
            try:
                actual = json.loads(payload)
            except Exception:
                actual = payload
        elif line == "___MUTATED_INPUT___":
            mutated = True
    return actual, mutated


def _normalize_val(val: any) -> any:
    if isinstance(val, (int, float, bool, list, dict, set, tuple)):
        return val
    if isinstance(val, str):
        val_str = val.strip()
        try:
            return ast.literal_eval(val_str)
        except Exception:
            return val_str
    return val


def _run_single_local(full_source: str, expected_raw: any, timeout: float) -> dict:
    import subprocess
    import sys
    import time

    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", full_source],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        if proc.returncode != 0:
            return {
                "outcome": "runtime_error",
                "actual_output": None,
                "duration_ms": duration_ms,
                "mutated": False,
            }

        actual_output, mutated = _parse_mutated_output(proc.stdout)
        if actual_output is None and proc.stdout.strip():
            for line in proc.stdout.splitlines():
                if not line.startswith("___MUTATED_INPUT___"):
                    actual_output = line.strip()
                    break

        norm_actual = _normalize_val(actual_output)
        norm_expected = _normalize_val(expected_raw)

        outcome = "passed" if norm_actual == norm_expected else "wrong_output"

        return {
            "outcome": outcome,
            "actual_output": actual_output,
            "duration_ms": duration_ms,
            "mutated": mutated,
        }
    except subprocess.TimeoutExpired:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "outcome": "timeout",
            "actual_output": None,
            "duration_ms": duration_ms,
            "mutated": False,
        }
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error("Local runner execution exception: %s", exc)
        return {
            "outcome": "runtime_error",
            "actual_output": None,
            "duration_ms": duration_ms,
            "mutated": False,
        }


async def _execute_local_fallback(source_code: str, test_cases: list[dict], timeout: float) -> list[dict]:
    # Fast syntax check
    try:
        ast.parse(source_code)
    except SyntaxError:
        return [
            {
                "test_case_id": tc["id"],
                "visibility": tc["visibility"],
                "outcome": "runtime_error",
                "actual_output": None,
                "duration_ms": 0,
                "mutated": False,
            }
            for tc in test_cases
        ]

    results = []
    for tc in test_cases:
        call = (tc.get("input_payload") or {}).get("call", "") or tc.get("description", "")
        full_source = _build_mutated_source(source_code, call)
        expected = tc.get("expected_output", "")

        res = await asyncio.to_thread(_run_single_local, full_source, expected, timeout)
        results.append({
            "test_case_id": tc["id"],
            "visibility": tc["visibility"],
            "outcome": res["outcome"],
            "actual_output": res["actual_output"] if tc["visibility"] == "visible" else None,
            "duration_ms": res.get("duration_ms"),
            "mutated": res.get("mutated", False),
        })
    return results


async def run_code(source_code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute source_code against each test_case via Judge0.
    Each result dict contains:
        test_case_id : str
        visibility   : "visible" | "hidden"
        outcome      : "passed" | "wrong_output" | "runtime_error" | "timeout"
        actual_output: any | None (only for visible tests)
        duration_ms  : int | None
        mutated      : bool — whether an input list was mutated
    """
    settings = get_settings()
    base_url = settings.runner_base_url.rstrip("/")
    api_key = settings.runner_api_key
    timeout = settings.runner_timeout_seconds

    if not api_key:
        logger.info("Judge0 API key not configured; using local runner fallback")
        return await _execute_local_fallback(source_code, test_cases, float(timeout))

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
            full_source = _build_mutated_source(source_code, call)
            expected = str(tc.get("expected_output", ""))

            try:
                token = await _submit(client, base_url, headers, full_source)
                result = await _poll(client, base_url, headers, token, timeout)
            except RunnerUnavailableError as rue:
                logger.warning("Judge0 unavailable (%s); falling back to local runner", rue)
                return await _execute_local_fallback(source_code, test_cases, float(timeout))
            except Exception as exc:
                logger.error("Judge0 execution failed for test %s: %s", tc.get("id"), exc)
                result = {"outcome": "runtime_error", "actual_output": None, "duration_ms": None, "mutated": False}

            outcome = result["outcome"]
            actual_output = result.get("actual_output")
            mutated = result.get("mutated", False)

            if outcome == "passed" and actual_output is not None:
                if str(actual_output).strip() != expected:
                    outcome = "wrong_output"

            results.append({
                "test_case_id": tc["id"],
                "visibility": tc["visibility"],
                "outcome": outcome,
                "actual_output": actual_output if tc["visibility"] == "visible" else None,
                "duration_ms": result.get("duration_ms"),
                "mutated": mutated,
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
                return {"outcome": "timeout", "actual_output": None, "duration_ms": None, "mutated": False}
            await asyncio.sleep(1)
            continue

        if status_id == STATUS_INTERNAL_ERROR:
            raise RunnerUnavailableError("Judge0 internal error.")

        outcome = _JUDGE0_TO_OUTCOME.get(status_id, "runtime_error")

        stdout = data.get("stdout") or ""
        actual_output, mutated = _parse_mutated_output(stdout)
        duration_ms = None
        try:
            duration_ms = int(float(data.get("time") or 0) * 1000)
        except (TypeError, ValueError):
            duration_ms = None

        return {
            "outcome": outcome,
            "actual_output": actual_output,
            "duration_ms": duration_ms,
            "mutated": mutated,
        }
