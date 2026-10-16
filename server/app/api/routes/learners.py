from fastapi import APIRouter, Depends
from supabase import Client

from app.integrations.supabase_client import get_supabase
from app.repositories.learners_repo import LearnersRepo
from app.schemas.learner import LearnerResponse, RecurringMistake, ConceptMastery, NextChallenge
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/learner", tags=["learner"])


@router.get("/{learner_id}", response_model=LearnerResponse)
async def get_learner(learner_id: str, db: Client = Depends(get_supabase)):
    repo = LearnersRepo(db)

    learner = repo.get_or_create(learner_id)
    learner_uuid = learner["id"]

    # Mastery
    raw_mastery = repo.get_concept_mastery(learner_uuid)
    mastery = [
        ConceptMastery(
            concept=row["concepts"]["slug"],
            estimate=round(float(row["mastery_score"]) / 100, 2),
        )
        for row in raw_mastery
    ]

    # Recurring mistakes (seen in ≥ 2 distinct challenges)
    raw_mistakes = repo.get_recurring_mistakes(learner_uuid)
    recurring = [
        RecurringMistake(category=r["slug"], challenge_count=r["challenge_count"])
        for r in raw_mistakes
        if r["challenge_count"] >= 2
    ]

    # Stub next-challenge recommendation — replace with LangGraph agent later
    next_challenge = None
    if recurring:
        next_challenge = NextChallenge(
            challenge_id="boundary-practice-01",
            reason=f"Practise '{recurring[0].category}', which appeared in {recurring[0].challenge_count} challenges.",
        )

    return LearnerResponse(
        learner_id=learner_id,
        recurring_mistakes=recurring,
        mastery=mastery,
        next_challenge=next_challenge,
    )
