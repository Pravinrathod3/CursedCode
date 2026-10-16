from functools import lru_cache
from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.local_db import LocalDBClient, init_db

logger = get_logger(__name__)


@lru_cache
def get_supabase():
    settings = get_settings()
    if (
        settings.supabase_url
        and settings.supabase_service_role_key
        and not settings.supabase_url.startswith("https://your-project")
        and settings.supabase_service_role_key != "replace_me"
    ):
        try:
            from supabase import create_client
            client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            client.table("concepts").select("id").limit(1).execute()
            return client
        except Exception as e:
            logger.warning("Could not reach Supabase, falling back to local SQLite DB: %s", e)

    # Initialize SQLite database with 17-schema.md DDL and seed data
    init_db()
    return LocalDBClient()

