"""Configuration utilities for data access."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DataConfig:
    """Environment-driven configuration used by data loaders."""

    supabase_url: str | None
    supabase_anon_key: str | None
    local_results_path: str



def load_data_config() -> DataConfig:
    """Load data configuration from environment variables."""

    return DataConfig(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
        local_results_path=os.getenv("LOCAL_RESULTS_PATH", "data/samples"),
    )
