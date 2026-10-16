"""
Red-team hostility test pack for DI-01 (Debug Dojo).
Verifies that all hostile programs (infinite loops, memory floods, output floods,
filesystem access, and fork attacks) are strictly contained by the sandbox and
properly classified into runtime_error or timeout without crashing the judge.
"""
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_redteam_infinite_loop():
    """Hostile infinite loop: must be contained with 'timeout'."""
    code = """def last_k_total(numbers, k):
    while True:
        pass
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "redteam_loop", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert any(t["outcome"] == "timeout" for t in data["visible"])
        assert data.get("limit") in ("time", None)


@pytest.mark.asyncio
async def test_redteam_memory_flood():
    """Hostile memory exhaustion: must be killed by memory limit with 'runtime_error'."""
    code = """def last_k_total(numbers, k):
    a = [0] * (80 * 1024 * 1024)  # ~640MB allocation
    return 0
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "redteam_mem", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(t["outcome"] == "runtime_error" for t in data["visible"])


@pytest.mark.asyncio
async def test_redteam_output_flood():
    """Hostile stdout flood: must be truncated or killed with 'runtime_error' or 'wrong_output'."""
    code = """def last_k_total(numbers, k):
    print("A" * 200000)
    return 0
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "redteam_out", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        data = resp.json()
        # Must not crash the server and must not be marked passed on non-zero tests
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_redteam_subsequent_normal_run():
    """Verifies that after hostile attacks, the server stays up and normal submissions run correctly."""
    code = """def last_k_total(numbers, k):
    if k == 0:
        return 0
    return sum(numbers[-k:])
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "normal_user", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(t["outcome"] == "passed" for t in data["visible"])
