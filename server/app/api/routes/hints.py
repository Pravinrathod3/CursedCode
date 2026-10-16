from fastapi import APIRouter, Depends
from app.integrations.supabase_client import get_supabase
from app.repositories.submissions_repo import SubmissionsRepo
from app.repositories.hints_repo import HintsRepo
from app.schemas.hint import HintRequest, HintResponse
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/hint", tags=["hints"])

MAX_HINTS = 4


@router.post("", response_model=HintResponse)
async def get_hint(body: HintRequest, db=Depends(get_supabase)):
    sub_repo = SubmissionsRepo(db)
    hints_repo = HintsRepo(db)

    sub = sub_repo.get_by_public_id(body.submission_id)

    current_hints = sub.get("hints_requested", 0)
    next_level = min(current_hints + 1, MAX_HINTS)

    hint_row = hints_repo.get_hint(sub["challenge_id"], next_level)

    if hint_row:
        hint_text = hint_row["hint_text"]
    else:
        hint_text = (
            "Try tracing through your code step by step with the visible test inputs. "
            "What does your function return versus what is expected?"
        )

    # Record that a hint was requested (server controls progression)
    sub_repo.update(sub["id"], {"hints_requested": next_level})

    return HintResponse(
        submission_id=body.submission_id,
        hint_index=next_level,
        level=next_level,
        remaining=max(0, MAX_HINTS - next_level),
        hint=hint_text,
    )
