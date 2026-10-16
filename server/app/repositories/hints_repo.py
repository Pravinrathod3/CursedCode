from app.core.logging import get_logger
from app.integrations.seed_challenges import SEED_CHALLENGES

logger = get_logger(__name__)

MAX_HINT_LEVEL = 4


class HintsRepo:
    def __init__(self, db):
        self.db = db

    def get_hint(self, challenge_id: str, hint_level: int, mistake_category_id: str | None = None) -> dict | None:
        try:
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
            if resp.data:
                return resp.data[0]
        except Exception as e:
            logger.warning("Could not fetch hint from table: %s", e)

        # Fallback to seed challenges
        try:
            # Resolve challenge slug
            ch_resp = self.db.table("challenges").select("slug").eq("id", challenge_id).execute()
            slug = ch_resp.data[0]["slug"] if ch_resp.data else challenge_id
        except Exception:
            slug = challenge_id

        seed = next((c for c in SEED_CHALLENGES if c["id"] == slug), None)
        if seed and "hints" in seed and len(seed["hints"]) >= hint_level:
            return {"hint_text": seed["hints"][hint_level - 1], "hint_level": hint_level}

        return None
