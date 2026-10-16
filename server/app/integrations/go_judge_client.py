"""
Integration client for criyle/go-judge high-performance sandbox execution engine.
Enforces strict cgroup/JobObject process isolation, CPU/clock limits, memory limits,
process limits, and output truncation.
"""
import json
import os
import shutil
import sys
import http
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def is_go_judge_available() -> bool:
    """Check if go-judge daemon is running and reachable."""
    settings = get_settings()
    if not settings.go_judge_enabled:
        return False
    try:
        with http.Client(timeout=0.6) as client:
            resp = client.get(f"{settings.go_judge_url}/version")
            return resp.status_code == 200
    except Exception:
        return False


def _resolve_sandbox_python() -> str:
    """
    Resolves the absolute path of the Python interpreter that the sandbox has permission to run.
    On Unix/macOS sandboxes, /usr/bin/python3 is universally readable.
    On Windows, python.exe is resolved via shutil.which or sys.executable.
    """
    if sys.platform == "win32":
        which_py = shutil.which("python.exe") or shutil.which("python")
        return which_py or sys.executable

    # Unix / macOS sandboxes
    for candidate in ["/usr/bin/python3", "/usr/local/bin/python3", shutil.which("python3"), sys.executable]:
        if candidate and os.path.exists(candidate):
            return candidate

    return sys.executable


async def run_in_go_judge(
    source_code: str,
    call_expr: str,
    timeout_seconds: float = 2.0,
    memory_limit_mb: int = 64,
) -> tuple[str, any, int, str | None]:
    """
    Executes learner code against a single test call using go-judge sandbox.
    Returns:
        (status, actual_output, duration_ms, limit_hit)
        status: 'ok' | 'wrong_output' | 'runtime_error' | 'timeout'
        limit_hit: 'time' | 'memory' | 'output' | None
    """
    settings = get_settings()
    python_bin = _resolve_sandbox_python()

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

    cpu_limit_ns = int(timeout_seconds * 1_000_000_000)
    clock_limit_ns = int((timeout_seconds + 1.0) * 1_000_000_000)
    mem_limit_bytes = int(memory_limit_mb * 1024 * 1024)

    payload = {
        "cmd": [
            {
                "args": [python_bin, "-c", script],
                "files": [
                    {"content": ""},
                    {"name": "stdout", "max": 65536},
                    {"name": "stderr", "max": 65536},
                ],
                "cpuLimit": cpu_limit_ns,
                "clockLimit": clock_limit_ns,
                "memoryLimit": mem_limit_bytes,
                "procLimit": 1,
            }
        ]
    }

    async with httpx.AsyncClient(timeout=timeout_seconds + 2.0) as client:
        resp = await client.post(f"{settings.go_judge_url}/run", json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"go-judge error {resp.status_code}: {resp.text}")

        res_list = resp.json()
        if not res_list or not isinstance(res_list, list):
            raise RuntimeError(f"Unexpected go-judge response: {res_list}")

        run_res = res_list[0]
        status = run_res.get("status", "Accepted")
        time_ns = run_res.get("time", 0)
        duration_ms = int(time_ns / 1_000_000)
        stdout = run_res.get("files", {}).get("stdout", "")

        if status == "Time Limit Exceeded":
            return "timeout", None, duration_ms, "time"

        if status == "Memory Limit Exceeded":
            return "runtime_error", None, duration_ms, "memory"

        if status == "Output Limit Exceeded":
            return "runtime_error", None, duration_ms, "output"

        if status in ("Nonzero Exit Code", "Signalled", "File Error"):
            return "runtime_error", None, duration_ms, None

        if status == "Accepted":
            for line in stdout.splitlines():
                if line.startswith("___OUT___"):
                    try:
                        actual = json.loads(line[9:])
                        return "ok", actual, duration_ms, None
                    except Exception:
                        return "ok", line[9:], duration_ms, None
            return "wrong_output", None, duration_ms, None

        # Any internal or unexpected error from sandbox
        err_msg = run_res.get("error", "Unknown sandbox error")
        raise RuntimeError(f"go-judge internal error: {err_msg}")
