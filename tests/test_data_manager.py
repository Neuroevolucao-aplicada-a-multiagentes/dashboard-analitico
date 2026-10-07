"""Tests for unified DataManager and Data Contract parity."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest
import pandas as pd

from app.data.data_contract import (
    CANONICAL_RUN_METRIC_COLUMNS,
    RUN_METRICS_FLOAT_COLUMNS,
    RUN_METRICS_INT_COLUMNS,
    standardize_run_metrics,
)
from app.data.data_manager import DataManager, get_run_data


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    """Create a temporary valid metrics CSV file."""
    content = (
        "geracao,fit_medio,fit_melhor,fit_pior,fit_std,coletas,entregas,colisoes,mortos,"
        "taxa_coleta,taxa_entrega,melhor_tempo,tempo_medio_entrega,distancia_media_entrega,"
        "taxa_mutacao_atual,forca_mutacao_atual,tempo_real_geracao_seg\n"
        "2,110.0,190.0,45.0,12.0,6,4,1,0,0.6,0.4,13.0,15.0,480.0,0.1,0.2,1.3\n"
        "1,90.0,160.0,35.0,10.0,4,2,0,0,0.4,0.2,15.0,18.0,550.0,0.1,0.2,1.2\n"
    )
    csv_file = tmp_path / "metricas.csv"
    csv_file.write_text(content, encoding="utf-8")
    return csv_file


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client returning matching run generation records."""
    mock_client = MagicMock()
    mock_query = MagicMock()
    mock_response = MagicMock()

    sample_generations = [
        {
            "id": "gen-uuid-2",
            "run_id": "87654321-4321-4321-4321-210987654321",
            "generation_number": 2,
            "population_size": 100,
            "best_fitness": 190.0,
            "average_fitness": 110.0,
            "worst_fitness": 45.0,
            "median_fitness": 105.0,
            "metrics": {
                "coletas": 6,
                "entregas": 4,
                "colisoes": 1,
                "mortos": 0,
                "taxa_coleta": 0.6,
                "taxa_entrega": 0.4,
                "melhor_tempo": 13.0,
                "tempo_medio_entrega": 15.0,
                "distancia_media_entrega": 480.0,
                "taxa_mutacao_atual": 0.1,
                "forca_mutacao_atual": 0.2,
                "tempo_real_geracao_seg": 1.3,
                "fit_std": 12.0,
            },
        },
        {
            "id": "gen-uuid-1",
            "run_id": "87654321-4321-4321-4321-210987654321",
            "generation_number": 1,
            "population_size": 100,
            "best_fitness": 160.0,
            "average_fitness": 90.0,
            "worst_fitness": 35.0,
            "median_fitness": 85.0,
            "metrics": {
                "coletas": 4,
                "entregas": 2,
                "colisoes": 0,
                "mortos": 0,
                "taxa_coleta": 0.4,
                "taxa_entrega": 0.2,
                "melhor_tempo": 15.0,
                "tempo_medio_entrega": 18.0,
                "distancia_media_entrega": 550.0,
                "taxa_mutacao_atual": 0.1,
                "forca_mutacao_atual": 0.2,
                "tempo_real_geracao_seg": 1.2,
                "fit_std": 10.0,
            },
        },
    ]

    mock_response.data = sample_generations
    mock_client.schema.return_value = mock_client
    mock_client.table.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.execute.return_value = mock_response

    return mock_client


def test_data_manager_loads_local_csv(sample_csv_path):
    manager = DataManager()
    df = manager.get_run_metrics(sample_csv_path, source="local")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.columns.tolist() == CANONICAL_RUN_METRIC_COLUMNS
    assert df["geracao"].tolist() == [1, 2]


def test_data_manager_loads_supabase(mock_supabase_client):
    run_uuid = "87654321-4321-4321-4321-210987654321"
    manager = DataManager(supabase_client=mock_supabase_client)
    df = manager.get_run_metrics(run_uuid, source="supabase")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.columns.tolist() == CANONICAL_RUN_METRIC_COLUMNS
    assert df["geracao"].tolist() == [1, 2]


def test_data_contract_parity_between_local_and_supabase(sample_csv_path, mock_supabase_client):
    """Core verification: Identical contract compliance across both data sources."""
    manager = DataManager(supabase_client=mock_supabase_client)

    df_local = manager.get_run_metrics(sample_csv_path, source="local")
    df_supabase = manager.get_run_metrics("87654321-4321-4321-4321-210987654321", source="supabase")

    # 1. Exact same column list and order
    assert df_local.columns.tolist() == df_supabase.columns.tolist()
    assert df_local.columns.tolist() == CANONICAL_RUN_METRIC_COLUMNS

    # 2. Exact same data types
    for col in RUN_METRICS_INT_COLUMNS:
        assert df_local[col].dtype.kind in ("i", "u"), f"{col} in df_local not int"
        assert df_supabase[col].dtype.kind in ("i", "u"), f"{col} in df_supabase not int"

    for col in RUN_METRICS_FLOAT_COLUMNS:
        assert df_local[col].dtype.kind == "f", f"{col} in df_local not float"
        assert df_supabase[col].dtype.kind == "f", f"{col} in df_supabase not float"

    # 3. Exact matching values across generations
    pd.testing.assert_frame_equal(df_local, df_supabase, check_dtype=True)


def test_auto_source_detection(sample_csv_path, mock_supabase_client):
    manager = DataManager(supabase_client=mock_supabase_client)

    # File path detected as local
    df_from_path = manager.get_run_metrics(sample_csv_path, source="auto")
    assert len(df_from_path) == 2

    # Valid UUID string detected as supabase
    df_from_uuid = manager.get_run_metrics("87654321-4321-4321-4321-210987654321", source="auto")
    assert len(df_from_uuid) == 2


def test_convenience_function_get_run_data(sample_csv_path):
    df = get_run_data(sample_csv_path, source="local")
    assert isinstance(df, pd.DataFrame)
    assert df.columns.tolist() == CANONICAL_RUN_METRIC_COLUMNS


def test_standardize_empty_and_nulls():
    empty_df = pd.DataFrame()
    standardized_empty = standardize_run_metrics(empty_df)
    assert standardized_empty.empty
    assert standardized_empty.columns.tolist() == CANONICAL_RUN_METRIC_COLUMNS
    for col in RUN_METRICS_INT_COLUMNS:
        assert standardized_empty[col].dtype.kind in ("i", "u")
    for col in RUN_METRICS_FLOAT_COLUMNS:
        assert standardized_empty[col].dtype.kind == "f"

    # Missing columns filled with proper defaults
    partial_df = pd.DataFrame([{"generation_number": 1, "best_fitness": 50.0}])
    standardized_partial = standardize_run_metrics(partial_df)
    assert standardized_partial["geracao"].iloc[0] == 1
    assert standardized_partial["fit_melhor"].iloc[0] == 50.0
    assert standardized_partial["coletas"].iloc[0] == 0
    assert standardized_partial["fit_pior"].iloc[0] == 0.0
