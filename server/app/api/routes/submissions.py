import uuid
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


def get_db(db=Depends(get_supabase)):
    return db


@router.post("", response_model=SubmitResponse)
async def submit(body: SubmitRequest, db=Depends(get_db)):
    challenges_repo = ChallengesRepo(db)
    submissions_repo = SubmissionsRepo(db)
    learners_repo = LearnersRepo(db)

    # Resolve learner (get or create)
    learner = learners_repo.get_or_create(body.learner_id)
    learner_uuid = learner["id"]

    # Resolve challenge
    challenge = challenges_repo.get_by_slug(body.challenge_id)
    challenge_uuid = challenge.get("uuid") or challenge["id"]

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
    limit_hit = None

    for i, (tc, res) in enumerate(zip(test_cases, raw_results), start=1):
        outcome = res["outcome"]
        vis = tc["visibility"]
        if res.get("limit_hit") and not limit_hit:
            limit_hit = res["limit_hit"]
        elif outcome == "timeout" and not limit_hit:
            limit_hit = "time"

        db_results.append(
            {
                "submission_id": sub_uuid,
                "test_case_id": tc["id"],
                "outcome": outcome,
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
                    expected=str(tc["expected_output"]) if outcome != "passed" else str(tc["expected_output"]),
                    got=str(res.get("actual_output")) if res.get("actual_output") is not None else None,
                    outcome=outcome,
                )
            )
        else:
            hidden_total += 1
            if outcome == "passed":
                hidden_passed += 1
            hidden_results.append(HiddenResult(test=i, outcome=outcome))

    overall_passed = (visible_passed == visible_total and hidden_passed == hidden_total)

    # Persist test results
    submissions_repo.insert_test_results(db_results)

    # Detect mistake categories
    mistake_tags = []
    if not overall_passed:
        # Check if print instead of return
        if any(r["outcome"] == "wrong_output" and (r.get("actual_output") is None or str(r.get("actual_output")).strip() == "None") for r in raw_results):
            mistake_tags.append("print_not_return")

        # Check for unhandled short input
        for tc, res in zip(test_cases, raw_results):
            desc = tc.get("description", "")
            if res["outcome"] != "passed" and ("[]" in desc or ", 0)" in desc or "(\"\")" in desc or "(0)" in desc or "([5])" in desc):
                mistake_tags.append("unhandled_short_input")
                break

        # Check for boundary comparison
        if "countpasses" in body.challenge_id:
            for tc, res in zip(test_cases, raw_results):
                if res["outcome"] != "passed" and "60" in tc.get("description", ""):
                    mistake_tags.append("boundary_comparison")
                    break

        # Check for mutates_input: function modified an input list
        if any(res.get("mutated") for res in raw_results):
            mistake_tags.append("mutates_input")

        if not mistake_tags:
            mistake_tags.append("off_by_one")

        # Record mistakes in database
        try:
            mistakes_to_insert = []
            for tag in mistake_tags:
                cat_resp = db.table("mistake_categories").select("id").eq("slug", tag).execute()
                if cat_resp.data:
                    mistakes_to_insert.append({
                        "submission_id": sub_uuid,
                        "mistake_category_id": cat_resp.data[0]["id"],
                        "confidence": 0.9,
                        "evidence_summary": f"Detected pattern: {tag}",
                        "detected_by": "rules"
                    })
            submissions_repo.insert_mistakes(mistakes_to_insert)
        except Exception as e:
            logger.warning("Could not persist submission mistakes: %s", e)

    # Update concept mastery
    try:
        from app.integrations.seed_challenges import SEED_CHALLENGES
        seed_match = next((c for c in SEED_CHALLENGES if c["id"] == body.challenge_id), None)
        tags = seed_match.get("tags", []) if seed_match else []

        for tag in tags:
            tag_slug = tag.lower()
            conc_resp = db.table("concepts").select("id").eq("slug", tag_slug).execute()
            if conc_resp.data:
                conc_id = conc_resp.data[0]["id"]
                # Query existing mastery
                cm_resp = db.table("concept_mastery").select("*").eq("learner_id", learner_uuid).eq("concept_id", conc_id).execute()
                if cm_resp.data:
                    cm = cm_resp.data[0]
                    attempts = cm.get("attempts", 0) + 1
                    successes = cm.get("successful_attempts", 0) + (1 if overall_passed else 0)
                    indep = cm.get("independent_successes", 0) + (1 if overall_passed else 0)
                    new_score = round(min(1.0, (successes * 0.7 + indep * 0.3) / max(1, attempts)) * 100, 1)
                    db.table("concept_mastery").update({
                        "attempts": attempts,
                        "successful_attempts": successes,
                        "independent_successes": indep,
                        "mastery_score": new_score,
                    }).eq("learner_id", learner_uuid).eq("concept_id", conc_id).execute()
                else:
                    score = 75.0 if overall_passed else 25.0
                    db.table("concept_mastery").insert({
                        "learner_id": learner_uuid,
                        "concept_id": conc_id,
                        "attempts": 1,
                        "successful_attempts": 1 if overall_passed else 0,
                        "independent_successes": 1 if overall_passed else 0,
                        "mastery_score": score,
                    }).execute()
    except Exception as e:
        logger.warning("Could not update concept mastery: %s", e)

    # Update submission record
    submissions_repo.update(
        sub_uuid,
        {
            "status": "completed",
            "visible_passed": visible_passed,
            "visible_total": visible_total,
            "hidden_passed": hidden_passed,
            "hidden_total": hidden_total,
            "overall_passed": 1 if overall_passed else 0,
            "resource_limit_hit": limit_hit,
        },
    )

    # Explanation text according to rules.md copy specifications
    failed_count = (visible_total - visible_passed) + (hidden_total - hidden_passed)
    total_count = visible_total + hidden_total
    if overall_passed:
        explanation = "All tests passed with no hints. Nice work."
    elif limit_hit:
        explanation = f"Execution stopped: {limit_hit} limit exceeded. Protect against unbounded resources."
    else:
        explanation = f"{failed_count} of {total_count} tests failed. Read what went wrong, then try again."

    return SubmitResponse(
        submission_id=public_id,
        learner_id=body.learner_id,
        challenge_id=body.challenge_id,
        visible=visible_results,
        hidden=hidden_results,
        mistake_tags=mistake_tags,
        explanation=explanation,
        limit=limit_hit,
    )
