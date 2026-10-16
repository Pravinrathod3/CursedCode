"""
Code execution runner client.
Executes learner code against test cases in an isolated sandbox.
Uses criyle/go-judge when available, with automatic fallback to isolated subprocess runner.
Guarantees hidden test inputs, outputs, and runner internals stay strictly server-side.
Classifies outcomes into exactly four states: passed, wrong_output, runtime_error, timeout.
"""
import ast
import asyncio
import json
import subprocess
import sys
import time
from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.go_judge_client import is_go_judge_available, run_in_go_judge

logger = get_logger(__name__)


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


def _execute_single_test_subprocess(
    source_code: str, call_expr: str, timeout_seconds: float = 2.0
) -> tuple[str, any, int, str | None]:
    """
    Fallback subprocess runner when go-judge is not running.
    Returns (outcome, actual_output, duration_ms, limit_hit).
    """
    script = f"""
import sys, json

{source_code}

try:
    _res = {call_expr}
    try:
        _out = json.dumps(_res)
    except Exception:
        _out = json.dumps(repr(_res))
    print("___OUT___" + _out)
except Exception as _e:
    print("___ERR___" + type(_e).__name__ + ": " + str(_e), file=sys.stderr)
    sys.exit(1)
"""
    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        if proc.returncode != 0:
            return "runtime_error", None, duration_ms, None

        for line in proc.stdout.splitlines():
            if line.startswith("___OUT___"):
                try:
                    actual = json.loads(line[9:])
                    return "ok", actual, duration_ms, None
                except Exception:
                    return "ok", line[9:], duration_ms, None

        return "wrong_output", None, duration_ms, None

    except subprocess.TimeoutExpired:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return "timeout", None, duration_ms, "time"
    except Exception as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error("Runner execution exception: %s", e)
        return "runtime_error", None, duration_ms, None


async def run_code(source_code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute source_code against each test_case dict and return results.
    Each result dict contains:
        test_case_id : str
        visibility   : "visible" | "hidden"
        outcome      : "passed" | "wrong_output" | "runtime_error" | "timeout"
        actual_output: any | None (only for visible tests)
        duration_ms  : int | None
        limit_hit    : "time" | "memory" | "output" | None
    """
    settings = get_settings()
    timeout = float(settings.runner_timeout_seconds)
    mem_limit = int(settings.go_judge_memory_limit_mb)
    use_go_judge = is_go_judge_available()

    if use_go_judge:
        logger.info("Using criyle/go-judge hardened sandbox runner")
    else:
        logger.info("go-judge not running; using isolated subprocess runner")

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
                "limit_hit": None,
            }
            for tc in test_cases
        ]

    results = []
    for tc in test_cases:
        call_expr = tc.get("description") or ""
        expected_raw = tc.get("expected_output")

        if not call_expr and "input_payload" in tc:
            try:
                payload = json.loads(tc["input_payload"]) if isinstance(tc["input_payload"], str) else tc["input_payload"]
                call_expr = payload.get("call", "")
            except Exception:
                pass

        if use_go_judge:
            try:
                status, actual, duration_ms, limit_hit = await run_in_go_judge(
                    source_code, call_expr, timeout_seconds=timeout, memory_limit_mb=mem_limit
                )
            except Exception as e:
                logger.warning("go-judge run error: %s; falling back to subprocess", e)
                status, actual, duration_ms, limit_hit = _execute_single_test_subprocess(
                    source_code, call_expr, timeout_seconds=timeout
                )
        else:
            status, actual, duration_ms, limit_hit = await asyncio.to_thread(
                _execute_single_test_subprocess, source_code, call_expr, timeout_seconds=timeout
            )

        if status == "ok":
            norm_actual = _normalize_val(actual)
            norm_expected = _normalize_val(expected_raw)
            outcome = "passed" if norm_actual == norm_expected else "wrong_output"
        elif status == "timeout":
            outcome = "timeout"
        else:
            outcome = "runtime_error"

        vis = tc.get("visibility", "hidden")
        safe_actual = str(actual) if vis == "visible" and actual is not None else None

        results.append({
            "test_case_id": tc["id"],
            "visibility": vis,
            "outcome": outcome,
            "actual_output": safe_actual,
            "duration_ms": duration_ms,
            "limit_hit": limit_hit,
        })

    return results
