"""
Mock / stub runner client.

Replace the body of `run_code` with a real HTTP call to the restricted runner
(e.g. Judge0 or a custom sandbox) before judging.
"""
import asyncio
import random
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_code(source_code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute source_code against each test_case dict and return results.

    Each result dict must contain:
        test_case_id : str
        visibility   : "visible" | "hidden"
        outcome      : "passed" | "wrong_output" | "runtime_error" | "timeout"
        actual_output: any | None   — only for visible tests
        duration_ms  : int | None
    """
    settings = get_settings()

    if settings.app_env != "development":
        raise NotImplementedError(
            "Live runner is not wired up yet. Set app_env=development to use the mock."
        )

    logger.warning("MOCK runner in use — do not use in production.")
    results = []
    for tc in test_cases:
        await asyncio.sleep(0)  # yield control
        outcome = random.choice(["passed", "passed", "wrong_output"])
        results.append(
            {
                "test_case_id": tc["id"],
                "visibility": tc["visibility"],
                "outcome": outcome,
                "actual_output": tc.get("expected_output") if outcome == "passed" else None,
                "duration_ms": random.randint(20, 120),
            }
        )
    return results
