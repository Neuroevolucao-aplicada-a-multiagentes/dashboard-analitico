"""Tests for fitness evolution visualization functions."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from app.data.data_contract import standardize_run_metrics
from app.visualizations.fitness_evolution import (
    build_fitness_evolution_figure,
    build_mutation_parameters_figure,
)


@pytest.fixture
def sample_metrics_df() -> pd.DataFrame:
    """Create a standardized metrics DataFrame with 5 generations."""
    data = {
        "geracao": [1, 2, 3, 4, 5],
        "fit_medio": [50.0, 70.0, 95.0, 110.0, 130.0],
        "fit_melhor": [90.0, 120.0, 150.0, 180.0, 210.0],
        "fit_pior": [10.0, 25.0, 40.0, 55.0, 70.0],
        "fit_std": [15.0, 12.0, 10.0, 8.0, 6.0],
        "taxa_mutacao_atual": [0.2, 0.18, 0.16, 0.14, 0.12],
        "forca_mutacao_atual": [0.4, 0.35, 0.3, 0.25, 0.2],
    }
    return standardize_run_metrics(pd.DataFrame(data))


def test_build_fitness_evolution_figure_structure(sample_metrics_df):
    """Test figure generation with complete traces (Best, Avg, Worst, Std Dev bounds)."""
    fig = build_fitness_evolution_figure(sample_metrics_df)

    assert isinstance(fig, go.Figure)
    trace_names = [trace.name for trace in fig.data]

    # Verify key traces are present
    assert "Melhor Fitness" in trace_names
    assert "Fitness Médio" in trace_names
    assert "Pior Fitness" in trace_names
    assert "Desvio Padrão (±1 std)" in trace_names

    # Check trace data lengths
    melhor_trace = next(t for t in fig.data if t.name == "Melhor Fitness")
    assert list(melhor_trace.y) == [90.0, 120.0, 150.0, 180.0, 210.0]
    assert list(melhor_trace.x) == [1, 2, 3, 4, 5]


def test_build_fitness_evolution_figure_zero_std():
    """Verify behavior when standard deviation is zero (skips shaded band cleanly)."""
    df = standardize_run_metrics(
        pd.DataFrame({
            "geracao": [1, 2],
            "fit_melhor": [100.0, 110.0],
            "fit_medio": [50.0, 60.0],
            "fit_pior": [10.0, 20.0],
            "fit_std": [0.0, 0.0],
        })
    )
    fig = build_fitness_evolution_figure(df)
    assert isinstance(fig, go.Figure)

    trace_names = [trace.name for trace in fig.data]
    assert "Melhor Fitness" in trace_names
    assert "Fitness Médio" in trace_names
    assert "Pior Fitness" in trace_names
    assert "Desvio Padrão (±1 std)" not in trace_names


def test_build_fitness_evolution_figure_empty():
    """Verify graceful handling of empty DataFrame without exceptions."""
    empty_df = pd.DataFrame()
    fig = build_fitness_evolution_figure(empty_df)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
    assert len(fig.layout.annotations) > 0


def test_build_mutation_parameters_figure(sample_metrics_df):
    """Test mutation hyperparameter chart creation."""
    fig = build_mutation_parameters_figure(sample_metrics_df)
    assert isinstance(fig, go.Figure)

    trace_names = [trace.name for trace in fig.data]
    assert "Taxa de Mutação" in trace_names
    assert "Força de Mutação" in trace_names


def test_build_mutation_parameters_figure_empty():
    """Test mutation chart with empty input."""
    fig = build_mutation_parameters_figure(pd.DataFrame())
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
