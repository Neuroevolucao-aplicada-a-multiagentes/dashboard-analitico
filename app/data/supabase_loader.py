"""Supabase loader for querying core tables from the database."""

import json
from typing import Any
import pandas as pd

from app.data.supabase_client import get_supabase_client

SCHEMA_CORE = "core"


def _resolve_client(client: Any | None = None) -> Any:
    """Resolve and validate the Supabase client instance."""
    active_client = client if client is not None else get_supabase_client()
    if active_client is None:
        raise RuntimeError(
            "Supabase client is not configured or unavailable. "
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment or .env file."
        )
    return active_client


def _get_table(client: Any, table_name: str, schema: str = SCHEMA_CORE) -> Any:
    """Obtain a query builder for the specified schema and table."""
    if hasattr(client, "schema") and callable(client.schema):
        return client.schema(schema).table(table_name)
    return client.table(table_name)


def _unpack_metrics_column(df: pd.DataFrame) -> pd.DataFrame:
    """Unpack JSONB 'metrics' dictionary into flat DataFrame columns."""
    if df.empty or "metrics" not in df.columns:
        return df

    df = df.copy()

    def parse_entry(val: Any) -> dict[str, Any]:
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}
        return {}

    metrics_records = df["metrics"].apply(parse_entry).tolist()
    metrics_df = pd.DataFrame(metrics_records, index=df.index)

    for col in metrics_df.columns:
        if col in df.columns:
            df[col] = metrics_df[col].combine_first(df[col])
        else:
            df[col] = metrics_df[col]

    return df


def load_experiments(client: Any | None = None) -> pd.DataFrame:
    """Fetch experiments from core.experiment.

    Args:
        client: Optional Supabase client instance (for testing/injection).

    Returns:
        pd.DataFrame with experiment records.
    """
    active_client = _resolve_client(client)
    builder = _get_table(active_client, "experiment").select("*").order("created_at")
    response = builder.execute()
    data = response.data if hasattr(response, "data") else []
    return pd.DataFrame(data)


def load_runs(
    experiment_id: str | None = None,
    client: Any | None = None,
) -> pd.DataFrame:
    """Fetch runs from core.run, optionally filtered by experiment_id.

    Args:
        experiment_id: Optional UUID filter for a specific experiment.
        client: Optional Supabase client instance.

    Returns:
        pd.DataFrame with run records.
    """
    active_client = _resolve_client(client)
    builder = _get_table(active_client, "run").select("*")
    if experiment_id is not None:
        builder = builder.eq("experiment_id", str(experiment_id))
    builder = builder.order("created_at")
    response = builder.execute()
    data = response.data if hasattr(response, "data") else []
    return pd.DataFrame(data)


def load_generations(
    run_id: str | None = None,
    client: Any | None = None,
    unpack_metrics: bool = True,
) -> pd.DataFrame:
    """Fetch generations from core.generation, optionally filtered by run_id.

    Extended metrics stored in the JSONB 'metrics' field are unpacked into
    individual columns when unpack_metrics is True.

    Note: To prevent severe network and memory overhead, this function queries
    only core.generation and never queries core.individual.

    Args:
        run_id: Optional UUID filter for a specific run.
        client: Optional Supabase client instance.
        unpack_metrics: If True (default), unpacks JSONB metrics into DataFrame columns.

    Returns:
        pd.DataFrame with generation records and unpacked extended metrics.
    """
    active_client = _resolve_client(client)
    builder = _get_table(active_client, "generation").select("*")
    if run_id is not None:
        builder = builder.eq("run_id", str(run_id))
    builder = builder.order("generation_number")
    response = builder.execute()
    data = response.data if hasattr(response, "data") else []
    df = pd.DataFrame(data)

    if unpack_metrics and not df.empty:
        df = _unpack_metrics_column(df)

    return df


def load_checkpoints(
    run_id: str | None = None,
    generation_id: str | None = None,
    client: Any | None = None,
) -> pd.DataFrame:
    """Fetch checkpoints from core.checkpoint.

    Args:
        run_id: Optional UUID filter for run.
        generation_id: Optional UUID filter for generation.
        client: Optional Supabase client instance.

    Returns:
        pd.DataFrame with checkpoint records.
    """
    active_client = _resolve_client(client)
    builder = _get_table(active_client, "checkpoint").select("*")
    if run_id is not None:
        builder = builder.eq("run_id", str(run_id))
    if generation_id is not None:
        builder = builder.eq("generation_id", str(generation_id))
    builder = builder.order("created_at")
    response = builder.execute()
    data = response.data if hasattr(response, "data") else []
    return pd.DataFrame(data)
