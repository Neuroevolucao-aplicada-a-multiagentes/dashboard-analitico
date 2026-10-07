"""Analytical metrics computations for execution and logistics performance."""

from typing import Any
import pandas as pd


def summarize_execution_metrics(execution_data: pd.DataFrame) -> dict[str, Any]:
    """Return a basic execution metrics summary."""
    if execution_data is None or execution_data.empty:
        return {"rows": 0, "columns": []}
    return {
        "rows": int(execution_data.shape[0]),
        "columns": list(execution_data.columns),
    }


def summarize_logistics_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Extract logistics KPIs for the latest generation and deltas from penultimate generation.

    Calculates key performance indicators including collection rate (taxa_coleta),
    delivery rate (taxa_entrega), collisions (colisoes), best delivery time (melhor_tempo),
    average delivery time, and distance, comparing against the previous generation.

    Args:
        df: Standardized DataFrame compliant with the Data Contract.

    Returns:
        dict: Summary containing latest generation KPIs and their deltas.
    """
    if df is None or df.empty:
        return {
            "total_generations": 0,
            "latest_generation": 0,
            "latest_taxa_coleta": 0.0,
            "delta_taxa_coleta": 0.0,
            "latest_taxa_entrega": 0.0,
            "delta_taxa_entrega": 0.0,
            "latest_colisoes": 0,
            "delta_colisoes": 0,
            "total_colisoes": 0,
            "latest_melhor_tempo": 0.0,
            "delta_melhor_tempo": 0.0,
            "latest_tempo_medio_entrega": 0.0,
            "delta_tempo_medio_entrega": 0.0,
            "latest_distancia_media_entrega": 0.0,
            "delta_distancia_media_entrega": 0.0,
            "latest_coletas": 0,
            "delta_coletas": 0,
            "latest_entregas": 0,
            "delta_entregas": 0,
            "latest_mortos": 0,
            "delta_mortos": 0,
            "has_delta": False,
        }

    sorted_df = df.sort_values(by="geracao").reset_index(drop=True)
    has_prev = len(sorted_df) > 1

    last_row = sorted_df.iloc[-1]
    prev_row = sorted_df.iloc[-2] if has_prev else last_row

    latest_gen = int(last_row.get("geracao", len(sorted_df)))

    # Taxa de Coleta
    latest_taxa_coleta = float(last_row.get("taxa_coleta", 0.0))
    prev_taxa_coleta = float(prev_row.get("taxa_coleta", 0.0))
    delta_taxa_coleta = (latest_taxa_coleta - prev_taxa_coleta) if has_prev else 0.0

    # Taxa de Entrega
    latest_taxa_entrega = float(last_row.get("taxa_entrega", 0.0))
    prev_taxa_entrega = float(prev_row.get("taxa_entrega", 0.0))
    delta_taxa_entrega = (latest_taxa_entrega - prev_taxa_entrega) if has_prev else 0.0

    # Colisões
    latest_colisoes = int(last_row.get("colisoes", 0))
    prev_colisoes = int(prev_row.get("colisoes", 0))
    delta_colisoes = (latest_colisoes - prev_colisoes) if has_prev else 0
    total_colisoes = int(sorted_df["colisoes"].sum()) if "colisoes" in sorted_df.columns else 0

    # Melhor Tempo
    latest_melhor_tempo = float(last_row.get("melhor_tempo", 0.0))
    prev_melhor_tempo = float(prev_row.get("melhor_tempo", 0.0))
    delta_melhor_tempo = (latest_melhor_tempo - prev_melhor_tempo) if has_prev else 0.0

    # Tempo Médio de Entrega
    latest_tempo_medio = float(last_row.get("tempo_medio_entrega", 0.0))
    prev_tempo_medio = float(prev_row.get("tempo_medio_entrega", 0.0))
    delta_tempo_medio = (latest_tempo_medio - prev_tempo_medio) if has_prev else 0.0

    # Distância Média de Entrega
    latest_distancia = float(last_row.get("distancia_media_entrega", 0.0))
    prev_distancia = float(prev_row.get("distancia_media_entrega", 0.0))
    delta_distancia = (latest_distancia - prev_distancia) if has_prev else 0.0

    # Contagens brutas (coletas, entregas, mortos)
    latest_coletas = int(last_row.get("coletas", 0))
    prev_coletas = int(prev_row.get("coletas", 0))
    delta_coletas = (latest_coletas - prev_coletas) if has_prev else 0

    latest_entregas = int(last_row.get("entregas", 0))
    prev_entregas = int(prev_row.get("entregas", 0))
    delta_entregas = (latest_entregas - prev_entregas) if has_prev else 0

    latest_mortos = int(last_row.get("mortos", 0))
    prev_mortos = int(prev_row.get("mortos", 0))
    delta_mortos = (latest_mortos - prev_mortos) if has_prev else 0

    return {
        "total_generations": len(sorted_df),
        "latest_generation": latest_gen,
        "latest_taxa_coleta": latest_taxa_coleta,
        "delta_taxa_coleta": delta_taxa_coleta,
        "latest_taxa_entrega": latest_taxa_entrega,
        "delta_taxa_entrega": delta_taxa_entrega,
        "latest_colisoes": latest_colisoes,
        "delta_colisoes": delta_colisoes,
        "total_colisoes": total_colisoes,
        "latest_melhor_tempo": latest_melhor_tempo,
        "delta_melhor_tempo": delta_melhor_tempo,
        "latest_tempo_medio_entrega": latest_tempo_medio,
        "delta_tempo_medio_entrega": delta_tempo_medio,
        "latest_distancia_media_entrega": latest_distancia,
        "delta_distancia_media_entrega": delta_distancia,
        "latest_coletas": latest_coletas,
        "delta_coletas": delta_coletas,
        "latest_entregas": latest_entregas,
        "delta_entregas": delta_entregas,
        "latest_mortos": latest_mortos,
        "delta_mortos": delta_mortos,
        "has_delta": has_prev,
    }
