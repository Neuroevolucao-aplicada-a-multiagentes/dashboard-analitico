"""Tests for training metrics analysis functions."""

import pandas as pd
from app.data.data_contract import standardize_run_metrics
from app.analysis.training_metrics import summarize_training_metrics


def test_summarize_training_metrics_populated():
    """Verify statistical computations on populated training DataFrame."""
    raw_df = pd.DataFrame({
        "geracao": [1, 2, 3],
        "fit_melhor": [100.0, 150.0, 220.0],
        "fit_medio": [60.0, 90.0, 130.0],
        "fit_pior": [20.0, 30.0, 40.0],
        "fit_std": [15.0, 12.0, 8.0],
        "coletas": [5, 10, 15],
        "entregas": [2, 5, 8],
    })
    df = standardize_run_metrics(raw_df)
    summary = summarize_training_metrics(df)

    assert summary["total_generations"] == 3
    assert summary["latest_generation"] == 3
    assert summary["best_fitness_overall"] == 220.0
    assert summary["latest_best_fitness"] == 220.0
    assert summary["latest_avg_fitness"] == 130.0
    assert summary["latest_worst_fitness"] == 40.0
    assert summary["latest_std_fitness"] == 8.0
    assert summary["delta_best"] == 70.0  # 220.0 - 150.0
    assert summary["delta_avg"] == 40.0   # 130.0 - 90.0
    assert summary["fitness_gain"] == 120.0  # 220.0 - 100.0
    assert summary["latest_collections"] == 15
    assert summary["latest_deliveries"] == 8


def test_summarize_training_metrics_empty():
    """Verify empty DataFrame gracefully returns default zero values."""
    empty_df = pd.DataFrame()
    summary = summarize_training_metrics(empty_df)

    assert summary["total_generations"] == 0
    assert summary["latest_generation"] == 0
    assert summary["best_fitness_overall"] == 0.0
    assert summary["latest_best_fitness"] == 0.0
    assert summary["fitness_gain"] == 0.0
    assert summary["rows"] == 0
