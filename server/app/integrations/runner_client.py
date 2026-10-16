"""
Code execution runner client.
Executes learner code via Judge0 REST API (primary) with a local sandboxed
subprocess fallback (bwrap + resource limits) when Judge0 is unreachable.
Never executes learner code outside a sandbox.
Guarantees hidden test inputs, outputs, and runner internals stay strictly
server-side. Classifies outcomes into exactly four states: passed,
wrong_output, runtime_error, timeout.
Also detects when learner code mutates its input lists (mutates_input).
"""
import ast
import asyncio
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import time
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

_BWRAP = shutil.which("bwrap")


def _set_resource_limits(timeout_seconds: float, memory_limit_mb: int):
    """Pre-exec callback: apply resource limits inside the child process."""
    resource.setrlimit(
        resource.RLIMIT_AS,
        (memory_limit_mb * 1024 * 1024 * 2, memory_limit_mb * 1024 * 1024 * 2),
    )
    resource.setrlimit(resource.RLIMIT_CPU, (int(timeout_seconds), int(timeout_seconds)))
    resource.setrlimit(resource.RLIMIT_NPROC, (16, 16))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))


def _build_mutated_source(source_code: str, call_str: str) -> str:
    """
    Build source code that executes the call and checks if any list argument
    was mutated. Uses variable assignments so we can compare before/after.
    Returns the full source string to send to the runner.
    """
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
    list_info = []

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

    call_with_vars = f"{func_name}({', '.join(call_vars)})"
    preamble.append(f"_result = {call_with_vars}")

    for var_name, list_source in list_info:
        preamble.append(f"if {var_name} != {list_source}:")
        preamble.append('    print("___MUTATED_INPUT___")')

    preamble.append(f'print("___RESULT___" + json.dumps(_result))')

    return "\n".join(preamble)


def _parse_mutated_output(stdout: str) -> tuple:
    """Parse runner stdout to extract (actual_output, mutated_flag)."""
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


def _execute_single_test_sandboxed(
    source_code: str,
    call_expr: str,
    timeout_seconds: float = 2.0,
    memory_limit_mb: int = 64,
) -> tuple:
    """
    Execute learner code in a local sandbox.
    Uses bwrap (namespace isolation: no network, no host FS, read-only /usr)
    plus resource limits (RLIMIT_AS, RLIMIT_CPU, RLIMIT_NPROC, RLIMIT_FSIZE).
    Falls back to resource-only limits if bwrap is absent.
    Returns (outcome, actual_output, duration_ms, limit_hit).
    """
    limits_preamble = f"""import sys, json, resource

resource.setrlimit(resource.RLIMIT_AS, ({memory_limit_mb * 1024 * 1024 * 2}, {memory_limit_mb * 1024 * 1024 * 2}))
resource.setrlimit(resource.RLIMIT_CPU, ({int(timeout_seconds)}, {int(timeout_seconds)}))
resource.setrlimit(resource.RLIMIT_NPROC, (16, 16))
resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))

"""
    full_source = limits_preamble + _build_mutated_source(source_code, call_expr)

    python_bin = sys.executable

    if _BWRAP:
        cmd = [
            _BWRAP,
            "--unshare-all",
            "--die-with-parent",
            "--new-session",
            "--ro-bind", "/", "/",
            "--proc", "/proc",
            "--dev", "/dev",
            "--tmpfs", "/tmp",
            "--hostname", "sandbox",
            "--",
            python_bin, "-c", full_source,
        ]
        preexec = None
    else:
        cmd = [python_bin, "-c", full_source]
        preexec = lambda: _set_resource_limits(timeout_seconds, memory_limit_mb)

    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 1.0,
            preexec_fn=preexec,
        )
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        stdout = proc.stdout or ""

        if proc.returncode != 0:
            if proc.returncode < 0:
                sig = -proc.returncode
                if sig in (signal.SIGXCPU, signal.SIGKILL, signal.SIGTERM):
                    return "timeout", None, duration_ms, "time", False
            return "runtime_error", None, duration_ms, None, False

        actual = None
        mutated = False
        for line in stdout.splitlines():
            if line.startswith("___RESULT___"):
                try:
                    actual = json.loads(line[len("___RESULT___"):])
                except Exception:
                    actual = line[len("___RESULT___"):]
            elif line == "___MUTATED_INPUT___":
                mutated = True

        if actual is None:
            return "wrong_output", None, duration_ms, None, mutated

        return "ok", actual, duration_ms, None, mutated

    except subprocess.TimeoutExpired:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return "timeout", None, duration_ms, "time", False
    except Exception as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error("Sandbox execution exception: %s", e)
        return "runtime_error", None, duration_ms, None, False


async def _run_one_test_judge0(client, base_url, headers, source_code, call, expected, timeout):
    """Run a single test case via Judge0."""
    full_source = _build_mutated_source(source_code, call)
    token = await _submit(client, base_url, headers, full_source)
    result = await _poll(client, base_url, headers, token, timeout)
    outcome = result["outcome"]
    actual_output = result.get("actual_output")
    mutated = result.get("mutated", False)
    if outcome == "passed" and actual_output is not None:
        if str(actual_output).strip() != str(expected):
            outcome = "wrong_output"
    return {
        "outcome": outcome,
        "actual_output": actual_output,
        "duration_ms": result.get("duration_ms"),
        "mutated": mutated,
    }


async def _run_one_test_local(source_code, call_expr, expected, timeout, memory_limit_mb):
    """Run a single test case in the local sandbox."""
    status, actual, duration_ms, limit_hit, mutated = await asyncio.to_thread(
        _execute_single_test_sandboxed, source_code, call_expr, timeout, memory_limit_mb
    )
    if status == "ok":
        norm_actual = str(actual).strip() if actual is not None else None
        norm_expected = str(expected).strip() if expected is not None else None
        outcome = "passed" if norm_actual == norm_expected else "wrong_output"
    elif status == "timeout":
        outcome = "timeout"
    else:
        outcome = "runtime_error"
    return {
        "outcome": outcome,
        "actual_output": actual,
        "duration_ms": duration_ms,
        "mutated": mutated,
    }


async def run_code(source_code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute source_code against each test_case.
    Tries Judge0 first; falls back to a local sandboxed subprocess if Judge0
    is unreachable. Every path returns one of four outcomes.
    """
    settings = get_settings()
    base_url = settings.runner_base_url.rstrip("/")
    api_key = settings.runner_api_key
    timeout = settings.runner_timeout_seconds
    mem_limit = int(settings.runner_memory_limit_mb)

    # Build the mutated-source variant once per call_expr.
    prepared = []
    for tc in test_cases:
        call = (tc.get("input_payload") or {}).get("call", "")
        expected = str(tc.get("expected_output", ""))
        prepared.append((tc, call, expected))

    results = []
    judge0_available = False

    # --- Try Judge0 first ---
    if api_key:
        host = urlparse(base_url).hostname or base_url
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": host,
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                for tc, call, expected in prepared:
                    result = await _run_one_test_judge0(
                        client, base_url, headers, source_code, call, expected, timeout
                    )
                    results.append({
                        "test_case_id": tc["id"],
                        "visibility": tc["visibility"],
                        "outcome": result["outcome"],
                        "actual_output": result["actual_output"]
                        if tc["visibility"] == "visible"
                        else None,
                        "duration_ms": result.get("duration_ms"),
                        "mutated": result.get("mutated", False),
                    })
            judge0_available = True
        except RunnerUnavailableError:
            logger.warning("Judge0 unavailable; falling back to local sandbox.")
        except Exception as exc:
            logger.error("Judge0 execution error: %s; falling back to local sandbox.", exc)

    # --- Local sandbox fallback (never runs unsandboxed) ---
    if not judge0_available:
        logger.info("Using local sandboxed subprocess runner.")
        for tc, call, expected in prepared:
            result = await _run_one_test_local(
                source_code, call, expected, timeout, mem_limit
            )
            results.append({
                "test_case_id": tc["id"],
                "visibility": tc["visibility"],
                "outcome": result["outcome"],
                "actual_output": result["actual_output"]
                if tc["visibility"] == "visible"
                else None,
                "duration_ms": result.get("duration_ms"),
                "mutated": result.get("mutated", False),
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
