from supabase import Client
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LearnersRepo:
    def __init__(self, db: Client):
        self.db = db

    def get_or_create(self, learner_key: str) -> dict:
        resp = (
            self.db.table("learners")
            .select("*")
            .eq("learner_key", learner_key)
            .execute()
        )
        if resp.data:
            row = resp.data[0]
            self.db.table("learners").update({"last_active_at": "now()"}).eq("id", row["id"]).execute()
            return row
        # Create new pseudonymous learner
        created = (
            self.db.table("learners")
            .insert({"learner_key": learner_key})
            .execute()
        )
        return created.data[0]

    def get_concept_mastery(self, learner_id: str) -> list[dict]:
        resp = (
            self.db.table("concept_mastery")
            .select("mastery_score, concept_id, concepts(slug, name)")
            .eq("learner_id", learner_id)
            .order("mastery_score", desc=False)
            .execute()
        )
        return resp.data or []

    def get_recurring_mistakes(self, learner_id: str) -> list[dict]:
        """Return mistake categories seen in >= 2 distinct challenges."""
        resp = (
            self.db.rpc(
                "get_recurring_mistakes",
                {"p_learner_id": learner_id},
            ).execute()
        )
        return resp.data or []
