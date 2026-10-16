from fastapi import APIRouter, Depends
from supabase import Client
from app.integrations.supabase_client import get_supabase
from app.repositories.challenges_repo import ChallengesRepo
from app.schemas.challenge import ChallengeListItem, ChallengeDetail

router = APIRouter(prefix="/challenges", tags=["challenges"])


def get_repo(db: Client = Depends(get_supabase)) -> ChallengesRepo:
    return ChallengesRepo(db)


@router.get("", response_model=list[ChallengeListItem])
async def list_challenges(learner_id: str | None = None, repo: ChallengesRepo = Depends(get_repo)):
    return repo.list_published(learner_id=learner_id)


@router.get("/{challenge_slug}", response_model=ChallengeDetail)
async def get_challenge(challenge_slug: str, repo: ChallengesRepo = Depends(get_repo)):
    return repo.get_by_slug(challenge_slug)
