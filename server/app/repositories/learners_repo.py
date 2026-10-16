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
        try:
            resp = (
                self.db.rpc(
                    "get_recurring_mistakes",
                    {"p_learner_id": learner_id},
                ).execute()
            )
            if resp.data:
                return resp.data
        except Exception:
            pass

        # Reliable standard query fallback without custom RPC
        try:
            subs_resp = self.db.table("submissions").select("id, challenge_id").eq("learner_id", learner_id).execute()
            sub_challenge_map = {s["id"]: s["challenge_id"] for s in subs_resp.data or []}
            if not sub_challenge_map:
                return []

            mistakes_by_cat = {}
            for sid, cid in sub_challenge_map.items():
                m_resp = self.db.table("submission_mistakes").select("mistake_category_id").eq("submission_id", sid).execute()
                for m in m_resp.data or []:
                    cat_id = m["mistake_category_id"]
                    if cat_id not in mistakes_by_cat:
                        mistakes_by_cat[cat_id] = set()
                    mistakes_by_cat[cat_id].add(cid)

            result = []
            for cat_id, distinct_challenges in mistakes_by_cat.items():
                if len(distinct_challenges) >= 2:
                    cat_resp = self.db.table("mistake_categories").select("slug").eq("id", cat_id).execute()
                    slug = cat_resp.data[0]["slug"] if cat_resp.data else str(cat_id)
                    result.append({"slug": slug, "challenge_count": len(distinct_challenges)})
            return result
        except Exception as e:
            logger.warning("Could not calculate recurring mistakes: %s", e)
            return []
