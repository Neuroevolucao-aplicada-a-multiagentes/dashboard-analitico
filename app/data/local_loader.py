"""Local data loader placeholder for offline/demo datasets."""

from pathlib import Path

from app.data.config import load_data_config



def get_local_results_path() -> Path:
    """Return base path for local result files.

    The path can be used by future loaders for CSV/Parquet/JSON artifacts.
    """

    config = load_data_config()
    return Path(config.local_results_path)
