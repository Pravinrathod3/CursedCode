import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_challenges():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/challenges?learner_id=test_user")
        assert resp.status_code == 200
        challenges = resp.json()
        assert len(challenges) >= 12
        first = challenges[0]
        assert "id" in first
        assert "title" in first
        assert "grade" in first
        assert "difficulty" in first
        assert "tags" in first
        assert "status" in first


@pytest.mark.asyncio
async def test_get_challenge_detail_public_fields_only():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/challenges/last-k-total")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "last-k-total"
        assert len(data["visibleTests"]) == 3
        assert data["hiddenTestCount"] == 5

        # Security check: verify no hidden test inputs or expected values are returned
        assert "hiddenTests" not in data
        assert "hidden_tests" not in data
        for vt in data["visibleTests"]:
            assert "test" in vt
            assert "call" in vt
            assert "expected" in vt


@pytest.mark.asyncio
async def test_submit_correct_solution():
    code = """def last_k_total(numbers, k):
    if k == 0:
        return 0
    return sum(numbers[-k:])
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "tester_1", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["submission_id"].startswith("sub_")
        assert len(result["visible"]) == 3
        assert len(result["hidden"]) == 5

        # All passed
        assert all(v["outcome"] == "passed" for v in result["visible"])
        assert all(h["outcome"] == "passed" for h in result["hidden"])

        # Security check: verify hidden results NEVER leak expected or got
        for h in result["hidden"]:
            assert "expected" not in h or h["expected"] is None
            assert "got" not in h or h["got"] is None
            assert "call" not in h or h["call"] is None


@pytest.mark.asyncio
async def test_submit_wrong_solution():
    code = """def last_k_total(numbers, k):
    return -999
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "tester_2", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        result = resp.json()
        assert any(v["outcome"] == "wrong_output" for v in result["visible"])
        assert any(h["outcome"] == "wrong_output" for h in result["hidden"])


@pytest.mark.asyncio
async def test_submit_runtime_error():
    code = """def last_k_total(numbers, k):
    return numbers[999]
"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/submit",
            json={"learner_id": "tester_3", "challenge_id": "last-k-total", "code": code}
        )
        assert resp.status_code == 200
        result = resp.json()
        assert any(v["outcome"] == "runtime_error" for v in result["visible"])


@pytest.mark.asyncio
async def test_progressive_hints_progression():
    code = "def last_k_total(numbers, k): return 0"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # First submit to get submission_id
        sub = await client.post(
            "/api/submit",
            json={"learner_id": "tester_hints", "challenge_id": "last-k-total", "code": code}
        )
        sub_id = sub.json()["submission_id"]

        # Request Hint 1
        h1 = await client.post("/api/hint", json={"submission_id": sub_id})
        assert h1.status_code == 200
        res1 = h1.json()
        assert res1["hint_index"] == 1
        assert res1["level"] == 1
        assert len(res1["hint"]) > 0

        # Request Hint 2
        h2 = await client.post("/api/hint", json={"submission_id": sub_id})
        assert h2.status_code == 200
        res2 = h2.json()
        assert res2["hint_index"] == 2
        assert res2["level"] == 2


@pytest.mark.asyncio
async def test_learner_profile():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/learner/zeroeight")
        assert resp.status_code == 200
        data = resp.json()
        assert data["learner_id"] == "zeroeight"
        assert len(data["mastery"]) == 6
        assert "next_challenge" in data
        assert data["next_challenge"] is not None
        assert "title" in data["next_challenge"]
