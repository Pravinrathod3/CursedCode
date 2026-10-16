from fastapi import APIRouter, Depends
from supabase import Client

from app.integrations.supabase_client import get_supabase
from app.repositories.challenges_repo import ChallengesRepo
from app.repositories.submissions_repo import SubmissionsRepo
from app.repositories.learners_repo import LearnersRepo
from app.integrations.runner_client import run_code
from app.schemas.submission import SubmitRequest, SubmitResponse, VisibleResult, HiddenResult
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/submit", tags=["submissions"])


def get_db(db: Client = Depends(get_supabase)) -> Client:
    return db


@router.post("", response_model=SubmitResponse)
async def submit(body: SubmitRequest, db: Client = Depends(get_db)):
    challenges_repo = ChallengesRepo(db)
    submissions_repo = SubmissionsRepo(db)
    learners_repo = LearnersRepo(db)

    # Resolve learner (get or create)
    learner = learners_repo.get_or_create(body.learner_id)
    learner_uuid = learner["id"]

    # Resolve challenge
    challenge = challenges_repo.get_by_slug(body.challenge_id)
    challenge_uuid = challenge["id"]

    # Fetch test cases (kept entirely server-side)
    test_cases = challenges_repo.get_test_cases(challenge_uuid)

    # Create pending submission record
    sub = submissions_repo.create(learner_uuid, challenge_uuid, body.code)
    sub_uuid = sub["id"]
    public_id = sub["public_id"]

    # Run code in sandbox
    raw_results = await run_code(body.code, test_cases)

    # Tally results
    visible_results: list[VisibleResult] = []
    hidden_results: list[HiddenResult] = []
    db_results = []
    visible_passed = visible_total = hidden_passed = hidden_total = 0

    for i, (tc, res) in enumerate(zip(test_cases, raw_results), start=1):
        outcome = res["outcome"]
        vis = tc["visibility"]

        db_results.append(
            {
                "submission_id": sub_uuid,
                "test_case_id": tc["id"],
                "outcome": outcome,
                # actual_output only safe for visible tests
                "actual_output": res.get("actual_output") if vis == "visible" else None,
                "duration_ms": res.get("duration_ms"),
            }
        )

        if vis == "visible":
            visible_total += 1
            if outcome == "passed":
                visible_passed += 1
            visible_results.append(
                VisibleResult(
                    test=i,
                    call=tc.get("description"),
                    expected=str(tc["expected_output"]) if outcome != "passed" else None,
                    got=str(res.get("actual_output")) if res.get("actual_output") is not None else None,
                    outcome=outcome,
                )
            )
        else:
            hidden_total += 1
            if outcome == "passed":
                hidden_passed += 1
            hidden_results.append(HiddenResult(test=i, outcome=outcome))

    overall_passed = visible_passed == visible_total and hidden_passed == hidden_total

    # Persist test results
    submissions_repo.insert_test_results(db_results)

    # Update submission record
    submissions_repo.update(
        sub_uuid,
        {
            "status": "completed",
            "visible_passed": visible_passed,
            "visible_total": visible_total,
            "hidden_passed": hidden_passed,
            "hidden_total": hidden_total,
            "overall_passed": overall_passed,
        },
    )

    return SubmitResponse(
        submission_id=public_id,
        learner_id=body.learner_id,
        challenge_id=body.challenge_id,
        visible=visible_results,
        hidden=hidden_results,
        mistake_tags=[],
        explanation=None,
    )
