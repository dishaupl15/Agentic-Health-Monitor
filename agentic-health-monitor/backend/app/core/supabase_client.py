from supabase import create_client, Client
from app.core.config import get_settings

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        s = get_settings()
        if not s.supabase_url.startswith("https://") or not s.supabase_key:
            raise RuntimeError("Set valid SUPABASE_URL and SUPABASE_KEY in backend .env")
        _client = create_client(s.supabase_url, s.supabase_key)
    return _client
