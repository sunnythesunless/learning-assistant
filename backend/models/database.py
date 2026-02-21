from supabase import create_client, Client
from core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        logger.info(f"[DB] Connecting to Supabase: {settings.SUPABASE_URL}")
        try:
            _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            logger.info("[DB] ✅ Supabase client created successfully")
        except Exception as e:
            logger.error(f"[DB] ❌ Failed to create Supabase client: {type(e).__name__}: {e}")
            raise
    return _client
