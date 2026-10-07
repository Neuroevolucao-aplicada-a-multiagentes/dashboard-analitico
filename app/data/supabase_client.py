"""Supabase client placeholder for repository data contracts."""

from typing import Any

from app.data.config import load_data_config



def get_supabase_client() -> Any | None:
    """Create and return a Supabase client when environment is configured.

    Returns None when required variables are missing. This placeholder keeps
    the dashboard decoupled from repository-internal implementations.
    """

    config = load_data_config()
    if not config.supabase_url or not config.supabase_anon_key:
        return None

    try:
        from supabase import Client, create_client
    except ImportError:
        return None

    client: Client = create_client(config.supabase_url, config.supabase_anon_key)
    return client
