"""Unit tests for Supabase data loader using mocks."""

from unittest.mock import MagicMock
import pytest
import pandas as pd

from app.data.supabase_loader import (
    load_checkpoints,
    load_experiments,
    load_generations,
    load_runs,
)


def _create_mock_client(data: list[dict]):
    """Helper to create a mocked Supabase client returning specified data."""
    mock_client = MagicMock()
    mock_query = MagicMock()
    mock_response = MagicMock()
    mock_response.data = data

    # Support chaining: .schema().table().select().eq().order().execute()
    mock_client.schema.return_value = mock_client
    mock_client.table.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.execute.return_value = mock_response

    return mock_client, mock_query


def test_load_experiments():
    sample_data = [
        {
            "id": "exp-1",
            "name": "Exp 1",
            "description": "Desc",
            "status": "completed",
            "metadata": {},
        }
    ]
    mock_client, mock_query = _create_mock_client(sample_data)

    df = load_experiments(client=mock_client)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["name"].iloc[0] == "Exp 1"
    mock_client.schema.assert_called_with("core")
    mock_client.table.assert_called_with("experiment")


def test_load_runs_with_filter():
    sample_data = [
        {
            "id": "run-10",
            "experiment_id": "exp-1",
            "phase_code": "fase_2",
            "run_label": "Run teste",
            "seed": 42,
            "status": "completed",
        }
    ]
    mock_client, mock_query = _create_mock_client(sample_data)

    df = load_runs(experiment_id="exp-1", client=mock_client)

    assert len(df) == 1
    assert df["phase_code"].iloc[0] == "fase_2"
    mock_client.table.assert_called_with("run")
    mock_query.eq.assert_called_with("experiment_id", "exp-1")


def test_load_generations_unpacks_jsonb_metrics():
    sample_data = [
        {
            "id": "gen-1",
            "run_id": "run-10",
            "generation_number": 1,
            "population_size": 100,
            "best_fitness": 120.5,
            "average_fitness": 75.0,
            "worst_fitness": 30.0,
            "median_fitness": 70.0,
            "metrics": {
                "coletas": 5,
                "entregas": 3,
                "colisoes": 1,
                "mortos": 0,
                "taxa_coleta": 0.5,
                "taxa_entrega": 0.3,
                "melhor_tempo": 14.2,
                "tempo_medio_entrega": 16.0,
                "distancia_media_entrega": 450.0,
                "taxa_mutacao_atual": 0.1,
                "forca_mutacao_atual": 0.2,
                "tempo_real_geracao_seg": 2.5,
                "fit_std": 12.3,
            },
        },
        {
            "id": "gen-2",
            "run_id": "run-10",
            "generation_number": 2,
            "population_size": 100,
            "best_fitness": 180.0,
            "average_fitness": 95.0,
            "worst_fitness": 40.0,
            "median_fitness": 90.0,
            "metrics": {
                "coletas": 8,
                "entregas": 6,
                "colisoes": 0,
                "mortos": 0,
                "taxa_coleta": 0.8,
                "taxa_entrega": 0.6,
                "melhor_tempo": 12.0,
                "tempo_medio_entrega": 14.5,
                "distancia_media_entrega": 420.0,
                "taxa_mutacao_atual": 0.1,
                "forca_mutacao_atual": 0.2,
                "tempo_real_geracao_seg": 2.2,
                "fit_std": 14.1,
            },
        },
    ]
    mock_client, mock_query = _create_mock_client(sample_data)

    df = load_generations(run_id="run-10", client=mock_client, unpack_metrics=True)

    assert len(df) == 2
    mock_client.table.assert_called_with("generation")
    mock_query.eq.assert_called_with("run_id", "run-10")

    # Verify extended JSONB metrics are extracted as DataFrame columns
    assert "coletas" in df.columns
    assert "entregas" in df.columns
    assert "taxa_coleta" in df.columns
    assert "distancia_media_entrega" in df.columns
    assert "fit_std" in df.columns
    assert df["coletas"].tolist() == [5, 8]
    assert df["entregas"].tolist() == [3, 6]


def test_load_generations_empty():
    mock_client, _ = _create_mock_client([])
    df = load_generations(run_id="run-empty", client=mock_client)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_checkpoints():
    sample_data = [
        {
            "id": "chk-1",
            "run_id": "run-10",
            "generation_id": "gen-1",
            "checkpoint_type": "best",
            "storage_path": "runs/run-10/best.npz",
            "fitness": 180.0,
        }
    ]
    mock_client, mock_query = _create_mock_client(sample_data)

    df = load_checkpoints(run_id="run-10", client=mock_client)

    assert len(df) == 1
    assert df["checkpoint_type"].iloc[0] == "best"
    mock_client.table.assert_called_with("checkpoint")
    mock_query.eq.assert_called_with("run_id", "run-10")


def test_client_missing_raises_runtime_error(monkeypatch):
    from app.data import supabase_loader

    # Force get_supabase_client to return None
    monkeypatch.setattr(supabase_loader, "get_supabase_client", lambda: None)

    with pytest.raises(RuntimeError, match="Supabase client is not configured"):
        load_experiments(client=None)


def test_no_query_touches_individual_table():
    """Verify strictly that core.individual is never queried by the loader."""
    mock_client, _ = _create_mock_client([])

    load_experiments(client=mock_client)
    load_runs(client=mock_client)
    load_generations(client=mock_client)
    load_checkpoints(client=mock_client)

    queried_tables = [call.args[0] for call in mock_client.table.call_args_list]
    assert "individual" not in queried_tables
    assert "core.individual" not in queried_tables
