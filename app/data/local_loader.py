"""Local data loader placeholder for offline/demo datasets."""

from pathlib import Path

from app.data.config import load_data_config
from app.data.sample_loader import load_metrics_csv

__all__ = ["get_local_results_path", "load_metrics_csv"]


def get_local_results_path() -> Path:
    """Return base path for local result files.

    The path can be used by future loaders for CSV/Parquet/JSON artifacts.
    """

    config = load_data_config()
    return Path(config.local_results_path)

