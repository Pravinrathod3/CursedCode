from collections import defaultdict

from supabase import Client
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LearnersRepo:
    def __init__(self, db):
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
            try:
                self.db.table("learners").update({"last_active_at": "now()"}).eq("id", row["id"]).execute()
            except Exception:
                pass
            return row

        # Create new pseudonymous learner
        created = (
            self.db.table("learners")
            .insert({"learner_key": learner_key})
            .execute()
        )
        return created.data[0]

    def get_concept_mastery(self, learner_id: str) -> list[dict]:
        try:
            resp = (
                self.db.table("concept_mastery")
                .select("mastery_score, concept_id, concepts(slug, name)")
                .eq("learner_id", learner_id)
                .order("mastery_score", desc=False)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            logger.warning("Could not fetch concept mastery: %s", e)
            return []

    def get_recurring_mistakes(self, learner_id: str) -> list[dict]:
        """Return mistake categories seen in >= 2 distinct challenges."""
        # Submission ids for this learner, mapped to their challenge.
        subs = (
            self.db.table("submissions")
            .select("id, challenge_id")
            .eq("learner_id", learner_id)
            .execute()
        )
        rows = subs.data or []
        if not rows:
            return []
        sub_ids = [r["id"] for r in rows]
        sub_to_challenge = {r["id"]: r["challenge_id"] for r in rows}

        # Mistake categories attached to those submissions.
        mistakes = (
            self.db.table("submission_mistakes")
            .select("submission_id, mistake_categories(slug)")
            .in_("submission_id", sub_ids)
            .execute()
        )

        cat_challenges: dict[str, set] = defaultdict(set)
        for m in (mistakes.data or []):
            cat = (m.get("mistake_categories") or {}).get("slug")
            if not cat:
                continue
            challenge_id = sub_to_challenge.get(m["submission_id"])
            if challenge_id:
                cat_challenges[cat].add(challenge_id)

        result = [
            {"slug": cat, "challenge_count": len(chals)}
            for cat, chals in cat_challenges.items()
            if len(chals) >= 2
        ]
        result.sort(key=lambda x: x["challenge_count"], reverse=True)
        return result
