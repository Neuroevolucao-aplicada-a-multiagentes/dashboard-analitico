"""Analytical metrics computations for training runs."""

from typing import Any
import pandas as pd


def summarize_training_metrics(training_data: pd.DataFrame) -> dict[str, Any]:
    """Calculate key summary statistics for a training run.

    Args:
        training_data: Standardized DataFrame compliant with the Data Contract.

    Returns:
        dict containing latest generation metrics, overall best fitness,
        deltas from previous generation, and overall progress.
    """
    if training_data is None or training_data.empty:
        return {
            "total_generations": 0,
            "latest_generation": 0,
            "best_fitness_overall": 0.0,
            "latest_best_fitness": 0.0,
            "latest_avg_fitness": 0.0,
            "latest_worst_fitness": 0.0,
            "latest_std_fitness": 0.0,
            "fitness_gain": 0.0,
            "avg_fitness_gain": 0.0,
            "delta_best": 0.0,
            "delta_avg": 0.0,
            "latest_collections": 0,
            "latest_deliveries": 0,
            "latest_collisions": 0,
            "latest_deaths": 0,
            "rows": 0,
            "columns": [],
        }

    df = training_data.sort_values(by="geracao").reset_index(drop=True)
    last_row = df.iloc[-1]
    first_row = df.iloc[0]
    prev_row = df.iloc[-2] if len(df) > 1 else last_row

    best_overall = float(df["fit_melhor"].max()) if "fit_melhor" in df.columns else 0.0
    latest_best = float(last_row.get("fit_melhor", 0.0))
    first_best = float(first_row.get("fit_melhor", 0.0))
    prev_best = float(prev_row.get("fit_melhor", 0.0))

    latest_avg = float(last_row.get("fit_medio", 0.0))
    first_avg = float(first_row.get("fit_medio", 0.0))
    prev_avg = float(prev_row.get("fit_medio", 0.0))

    latest_worst = float(last_row.get("fit_pior", 0.0))
    latest_std = float(last_row.get("fit_std", 0.0))

    delta_best = latest_best - prev_best if len(df) > 1 else 0.0
    delta_avg = latest_avg - prev_avg if len(df) > 1 else 0.0
    fitness_gain = latest_best - first_best
    avg_fitness_gain = latest_avg - first_avg

    return {
        "total_generations": len(df),
        "latest_generation": int(last_row.get("geracao", len(df))),
        "best_fitness_overall": best_overall,
        "latest_best_fitness": latest_best,
        "latest_avg_fitness": latest_avg,
        "latest_worst_fitness": latest_worst,
        "latest_std_fitness": latest_std,
        "fitness_gain": fitness_gain,
        "avg_fitness_gain": avg_fitness_gain,
        "delta_best": delta_best,
        "delta_avg": delta_avg,
        "latest_collections": int(last_row.get("coletas", 0)),
        "latest_deliveries": int(last_row.get("entregas", 0)),
        "latest_collisions": int(last_row.get("colisoes", 0)),
        "latest_deaths": int(last_row.get("mortos", 0)),
        "rows": int(df.shape[0]),
        "columns": list(df.columns),
    }
