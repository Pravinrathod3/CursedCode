from fastapi import APIRouter, Depends
from app.integrations.supabase_client import get_supabase
from app.repositories.learners_repo import LearnersRepo
from app.repositories.challenges_repo import ChallengesRepo
from app.schemas.learner import LearnerResponse, RecurringMistake, ConceptMastery, NextChallenge
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/learner", tags=["learner"])

STANDARD_CONCEPTS = [
    ("Lists", "lists"),
    ("Loops", "loops"),
    ("Strings", "strings"),
    ("Slicing", "slicing"),
    ("Indexing", "indexing"),
    ("Comparison", "comparison")
]


def score_to_grade_and_difficulty(score: float) -> tuple[str, str]:
    """Derives grade and difficulty according to client/docs/rules.md 2.2."""
    if score < 0.20:
        return "Grade 4", "Easy"
    elif score < 0.40:
        return "Grade 3", "Medium"
    elif score < 0.60:
        return "Grade 2", "Hard"
    elif score < 0.80:
        return "Semi-Grade 1", "Advanced"
    elif score < 0.93:
        return "Grade 1", "Expert"
    else:
        return "Special Grade", "Supreme"


@router.get("/{learner_id}", response_model=LearnerResponse)
async def get_learner(learner_id: str, db=Depends(get_supabase)):
    repo = LearnersRepo(db)
    challenges_repo = ChallengesRepo(db)

    learner = repo.get_or_create(learner_id)
    learner_uuid = learner["id"]

    # Raw mastery from db
    raw_mastery = repo.get_concept_mastery(learner_uuid)
    mastery_map = {}
    for row in raw_mastery:
        slug = row.get("concepts", {}).get("slug") if isinstance(row.get("concepts"), dict) else None
        if slug:
            mastery_map[slug.lower()] = round(float(row.get("mastery_score", 0)) / 100, 2)

    mastery_list = []
    for display_name, slug in STANDARD_CONCEPTS:
        est = mastery_map.get(slug, 0.0)
        grade, diff = score_to_grade_and_difficulty(est)
        mastery_list.append(
            ConceptMastery(
                concept=display_name,
                estimate=est,
                score=est,
                grade=grade,
                difficulty=diff
            )
        )

    # Recurring mistakes (seen in ≥ 2 distinct challenges)
    raw_mistakes = repo.get_recurring_mistakes(learner_uuid)
    recurring = [
        RecurringMistake(category=r["slug"], challenge_count=r["challenge_count"])
        for r in raw_mistakes
        if r.get("challenge_count", 0) >= 2
    ]

    # Next challenge recommendation
    published_challenges = challenges_repo.list_published(learner_id=learner_id)
    # Pick first unsolved challenge
    unsolved = [c for c in published_challenges if c.get("status") != "Solved"]
    target = unsolved[0] if unsolved else (published_challenges[0] if published_challenges else None)

    next_challenge = None
    if target:
        if recurring:
            reason = f"Practise '{recurring[0].category}', which appeared across {recurring[0].challenge_count} different trials."
        else:
            reason = f"Reinforcing boundary conditions in '{target['title']}' will solidify your core algorithmic foundation."

        next_challenge = NextChallenge(
            challenge_id=target["slug"],
            title=target["title"],
            grade=target.get("grade", "Grade 4"),
            difficulty=target.get("difficulty", "Easy"),
            reason=reason
        )

    return LearnerResponse(
        learner_id=learner_id,
        recurring_mistakes=recurring,
        mastery=mastery_list,
        next_challenge=next_challenge,
    )
