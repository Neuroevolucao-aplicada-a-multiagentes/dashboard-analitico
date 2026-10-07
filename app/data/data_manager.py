"""Unified data access manager (Data Contract facade).

This module abstracts the data source (local CSV files vs Supabase database).
The analytical layer can request data for a run and receive a standardized DataFrame
with identical columns, data types, and sorting regardless of the source.
"""

from pathlib import Path
from typing import Any, Literal
import uuid
import pandas as pd

from app.data.config import DataConfig, load_data_config
from app.data.data_contract import (
    CANONICAL_RUN_METRIC_COLUMNS,
    RUN_METRICS_FLOAT_COLUMNS,
    RUN_METRICS_INT_COLUMNS,
    standardize_run_metrics,
)
from app.data.sample_loader import load_metrics_csv
from app.data.supabase_loader import (
    load_checkpoints,
    load_experiments,
    load_generations,
    load_runs,
)

SourceType = Literal["auto", "local", "supabase"]


class DataManager:
    """Unified facade managing data access across local files and Supabase."""

    def __init__(
        self,
        config: DataConfig | None = None,
        supabase_client: Any | None = None,
    ) -> None:
        """Initialize DataManager.

        Args:
            config: Optional DataConfig instance.
            supabase_client: Optional injected Supabase client (e.g. for testing).
        """
        self.config = config or load_data_config()
        self._supabase_client = supabase_client

    @property
    def supabase_client(self) -> Any | None:
        """Return the active Supabase client instance if configured."""
        if self._supabase_client is not None:
            return self._supabase_client
        from app.data.supabase_client import get_supabase_client

        return get_supabase_client()

    def get_run_metrics(
        self,
        run_identifier: str | Path,
        source: SourceType = "auto",
        preserve_extra_columns: bool = False,
    ) -> pd.DataFrame:
        """Fetch standardized run metrics according to the Data Contract.

        Args:
            run_identifier: File path to a CSV (for local) or UUID string (for Supabase).
            source: Source selector ('auto', 'local', or 'supabase').
            preserve_extra_columns: If True, keep extra columns beyond canonical ones.

        Returns:
            Standardized pd.DataFrame with guaranteed columns, types and sorting.

        Raises:
            ValueError: If source is invalid or run cannot be found/loaded.
            FileNotFoundError: If a requested local file does not exist.
        """
        resolved_source = self._resolve_source(run_identifier, source)

        if resolved_source == "local":
            raw_df = self._load_from_local(run_identifier)
        elif resolved_source == "supabase":
            raw_df = self._load_from_supabase(run_identifier)
        else:
            raise ValueError(f"Fonte desconhecida: {resolved_source}")

        return standardize_run_metrics(raw_df, preserve_extra_columns=preserve_extra_columns)

    def _resolve_source(
        self,
        identifier: str | Path,
        source: SourceType,
    ) -> Literal["local", "supabase"]:
        """Determine whether an identifier refers to a local file or Supabase."""
        if source in ("local", "supabase"):
            return source

        # Auto-detection heuristic:
        # If it's a Path object, or exists on disk, or ends with .csv, treat as local
        identifier_path = Path(identifier)
        if identifier_path.is_file() or str(identifier).lower().endswith(".csv"):
            return "local"

        # Check if it looks like a UUID
        try:
            uuid.UUID(str(identifier))
            return "supabase"
        except (ValueError, AttributeError):
            pass

        # Check if path relative to local results directory exists
        base_path = Path(self.config.local_results_path)
        if (base_path / identifier).is_file():
            return "local"

        # Default to supabase if client is configured, otherwise local
        if self.supabase_client is not None:
            return "supabase"
        return "local"

    def _load_from_local(self, identifier: str | Path) -> pd.DataFrame:
        """Load metrics from a local CSV file."""
        target_path = Path(identifier)
        if not target_path.is_file():
            # Check relative to configured local_results_path
            candidate = Path(self.config.local_results_path) / identifier
            if candidate.is_file():
                target_path = candidate
            elif (candidate / "metricas.csv").is_file():
                target_path = candidate / "metricas.csv"

        return load_metrics_csv(target_path)

    def _load_from_supabase(self, run_id: str | Path) -> pd.DataFrame:
        """Load generations metrics from Supabase core.generation."""
        client = self.supabase_client
        if client is None:
            raise RuntimeError(
                "Cliente Supabase não está disponível para carregar a run. "
                "Configure SUPABASE_URL e SUPABASE_ANON_KEY."
            )
        return load_generations(run_id=str(run_id), client=client, unpack_metrics=True)

    # Convenience exploration methods
    def list_experiments(self) -> pd.DataFrame:
        """List experiments from Supabase."""
        return load_experiments(client=self.supabase_client)

    def list_runs(self, experiment_id: str | None = None) -> pd.DataFrame:
        """List runs from Supabase."""
        return load_runs(experiment_id=experiment_id, client=self.supabase_client)

    def list_checkpoints(self, run_id: str | None = None) -> pd.DataFrame:
        """List checkpoints from Supabase."""
        return load_checkpoints(run_id=run_id, client=self.supabase_client)


# Module-level convenience functions
_default_manager: DataManager | None = None


def get_data_manager(supabase_client: Any | None = None) -> DataManager:
    """Return a singleton or newly initialized DataManager instance."""
    global _default_manager
    if supabase_client is not None:
        return DataManager(supabase_client=supabase_client)
    if _default_manager is None:
        _default_manager = DataManager()
    return _default_manager


def get_run_data(
    run_identifier: str | Path,
    source: SourceType = "auto",
    client: Any | None = None,
    preserve_extra_columns: bool = False,
) -> pd.DataFrame:
    """Convenience function to fetch standardized run data from any source."""
    manager = get_data_manager(supabase_client=client)
    return manager.get_run_metrics(
        run_identifier,
        source=source,
        preserve_extra_columns=preserve_extra_columns,
    )
