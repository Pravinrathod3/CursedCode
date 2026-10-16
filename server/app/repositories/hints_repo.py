from supabase import Client
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)

MAX_HINT_LEVEL = 5


class HintsRepo:
    def __init__(self, db: Client):
        self.db = db

    def get_hint(self, challenge_id: str, hint_level: int, mistake_category_id: str | None = None) -> dict | None:
        query = (
            self.db.table("challenge_hints")
            .select("hint_text, hint_level")
            .eq("challenge_id", challenge_id)
            .eq("hint_level", hint_level)
            .eq("is_active", True)
        )
        if mistake_category_id:
            query = query.eq("mistake_category_id", mistake_category_id)
        else:
            query = query.is_("mistake_category_id", None)

        resp = query.limit(1).execute()
        return resp.data[0] if resp.data else None
