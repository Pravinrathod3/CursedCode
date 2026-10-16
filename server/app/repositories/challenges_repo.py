from supabase import Client
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChallengesRepo:
    def __init__(self, db: Client):
        self.db = db

    def list_published(self) -> list[dict]:
        resp = (
            self.db.table("challenges")
            .select("id, slug, title, difficulty, sort_order")
            .eq("is_published", True)
            .order("sort_order")
            .execute()
        )
        return resp.data or []

    def get_by_slug(self, slug: str) -> dict:
        resp = (
            self.db.table("challenges")
            .select("id, slug, title, statement, function_signature, starter_code, difficulty, sort_order")
            .eq("slug", slug)
            .eq("is_published", True)
            .single()
            .execute()
        )
        if not resp.data:
            raise NotFoundError(f"Challenge '{slug}' not found.")
        return resp.data

    def get_test_cases(self, challenge_id: str) -> list[dict]:
        """Returns ALL test cases (visible + hidden) — never send to frontend."""
        resp = (
            self.db.table("test_cases")
            .select("id, visibility, ordinal, input_payload, expected_output, timeout_ms, description")
            .eq("challenge_id", challenge_id)
            .order("ordinal")
            .execute()
        )
        return resp.data or []
