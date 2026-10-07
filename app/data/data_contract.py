"""Data Contract definitions and standardization utilities for the analytical layer."""

from typing import Sequence
import pandas as pd

RUN_METRICS_INT_COLUMNS: list[str] = [
    "geracao",
    "coletas",
    "entregas",
    "colisoes",
    "mortos",
]

RUN_METRICS_FLOAT_COLUMNS: list[str] = [
    "fit_medio",
    "fit_melhor",
    "fit_pior",
    "fit_std",
    "taxa_coleta",
    "taxa_entrega",
    "melhor_tempo",
    "tempo_medio_entrega",
    "distancia_media_entrega",
    "taxa_mutacao_atual",
    "forca_mutacao_atual",
    "tempo_real_geracao_seg",
]

CANONICAL_RUN_METRIC_COLUMNS: list[str] = (
    RUN_METRICS_INT_COLUMNS + RUN_METRICS_FLOAT_COLUMNS
)


def standardize_run_metrics(
    df: pd.DataFrame,
    preserve_extra_columns: bool = False,
) -> pd.DataFrame:
    """Standardize a run metrics DataFrame according to the Data Contract.

    Ensures column names, types (int/float), and sorting (by 'geracao' ascending)
    match the canonical contract whether sourced from local CSV or Supabase.

    Args:
        df: Input DataFrame with raw or partially structured metrics.
        preserve_extra_columns: If True, extra non-contract columns are kept after
            the canonical columns. If False (default), only canonical columns are returned.

    Returns:
        pd.DataFrame strictly compliant with the canonical run metrics contract.
    """
    if df.empty:
        # Create empty typed DataFrame matching the canonical contract
        empty_dict: dict[str, Sequence] = {
            col: pd.Series(dtype="int64") for col in RUN_METRICS_INT_COLUMNS
        }
        empty_dict.update({
            col: pd.Series(dtype="float64") for col in RUN_METRICS_FLOAT_COLUMNS
        })
        return pd.DataFrame(empty_dict)[CANONICAL_RUN_METRIC_COLUMNS]

    standardized = df.copy()
    standardized.columns = standardized.columns.astype(str).str.strip()

    # Column aliases resolution (e.g. from Supabase core.generation schema)
    alias_map = {
        "generation_number": "geracao",
        "best_fitness": "fit_melhor",
        "average_fitness": "fit_medio",
        "worst_fitness": "fit_pior",
    }
    for db_col, canonical_col in alias_map.items():
        if canonical_col not in standardized.columns and db_col in standardized.columns:
            standardized[canonical_col] = standardized[db_col]
        elif canonical_col in standardized.columns and db_col in standardized.columns:
            # Fill missing/null canonical values with the database column values
            standardized[canonical_col] = standardized[canonical_col].fillna(standardized[db_col])

    # Enforce integer columns with 0 default
    for col in RUN_METRICS_INT_COLUMNS:
        if col not in standardized.columns:
            standardized[col] = 0
        else:
            standardized[col] = pd.to_numeric(standardized[col], errors="coerce").fillna(0).astype(int)

    # Enforce float columns with 0.0 default
    for col in RUN_METRICS_FLOAT_COLUMNS:
        if col not in standardized.columns:
            standardized[col] = 0.0
        else:
            standardized[col] = pd.to_numeric(standardized[col], errors="coerce").fillna(0.0).astype(float)

    # Sort strictly by geracao ascending
    standardized = standardized.sort_values(by="geracao").reset_index(drop=True)

    if preserve_extra_columns:
        extra_cols = [c for c in standardized.columns if c not in CANONICAL_RUN_METRIC_COLUMNS]
        return standardized[CANONICAL_RUN_METRIC_COLUMNS + extra_cols]

    return standardized[CANONICAL_RUN_METRIC_COLUMNS]
