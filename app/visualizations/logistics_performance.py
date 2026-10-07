"""Logistics performance visualizations for warehouse operation analysis.

Provides Plotly figures for operational evolution (pickups, deliveries, deaths, collisions)
and logistics efficiency (mean delivery time, best time, mean delivery distance)
according to the canonical Data Contract.
"""

from typing import Any
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_operational_evolution_figure(
    execution_data: pd.DataFrame,
    title: str = "Evolução Operacional por Geração",
) -> go.Figure:
    """Build a chart illustrating operational evolution across generations.

    Plots total collections (coletas), successful deliveries (entregas),
    agent deaths (mortos), and warehouse collisions (colisoes) across generations.

    Args:
        execution_data: Standardized DataFrame compliant with the Data Contract.
        title: Title of the generated chart.

    Returns:
        go.Figure: Interactive Plotly figure.
    """
    fig = go.Figure()

    if execution_data is None or execution_data.empty:
        fig.add_annotation(
            text="Nenhum dado operacional disponível para visualização.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", x=0.02, font=dict(size=16)),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template="plotly_white",
        )
        return fig

    df = execution_data.copy()
    for col in ["geracao", "coletas", "entregas", "colisoes", "mortos"]:
        if col not in df.columns:
            df[col] = 0 if col != "geracao" else range(1, len(df) + 1)

    generations = df["geracao"]

    # 1. Coletas
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["coletas"],
            mode="lines+markers",
            name="Coletas",
            line=dict(color="#2E7D32", width=2.5),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Coletas: %{y}<extra></extra>",
        )
    )

    # 2. Entregas
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["entregas"],
            mode="lines+markers",
            name="Entregas",
            line=dict(color="#1976D2", width=2.5),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Entregas: %{y}<extra></extra>",
        )
    )

    # 3. Colisões
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["colisoes"],
            mode="lines+markers",
            name="Colisões",
            line=dict(color="#FB8C00", width=2, dash="dash"),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Colisões: %{y}<extra></extra>",
        )
    )

    # 4. Mortos
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["mortos"],
            mode="lines+markers",
            name="Mortos",
            line=dict(color="#E53935", width=2, dash="dot"),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Mortos: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02,
            font=dict(size=16),
        ),
        xaxis=dict(
            title="Geração",
            gridcolor="#F0F0F0",
            dtick=1 if len(generations) <= 20 else None,
        ),
        yaxis=dict(
            title="Contagem Operacional",
            gridcolor="#F0F0F0",
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig


def build_efficiency_time_figure(
    execution_data: pd.DataFrame,
    title: str = "Eficiência e Tempo de Operação por Geração",
) -> go.Figure:
    """Build a chart tracking delivery times and average travel distance.

    Plots average delivery time (tempo_medio_entrega) and best delivery time
    (melhor_tempo) on the primary axis, with average delivery distance
    (distancia_media_entrega) on the secondary axis.

    Args:
        execution_data: Standardized DataFrame compliant with the Data Contract.
        title: Title of the generated chart.

    Returns:
        go.Figure: Interactive Plotly figure with dual y-axes.
    """
    if execution_data is None or execution_data.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_annotation(
            text="Nenhum dado de eficiência disponível para visualização.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", x=0.02, font=dict(size=16)),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template="plotly_white",
        )
        return fig

    df = execution_data.copy()
    for col in ["tempo_medio_entrega", "melhor_tempo", "distancia_media_entrega"]:
        if col not in df.columns:
            df[col] = 0.0

    if "geracao" not in df.columns:
        df["geracao"] = range(1, len(df) + 1)

    generations = df["geracao"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Tempo Médio de Entrega (Primary Y)
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["tempo_medio_entrega"],
            mode="lines+markers",
            name="Tempo Médio (s)",
            line=dict(color="#0288D1", width=2.5),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Tempo Médio: %{y:.2f}s<extra></extra>",
        ),
        secondary_y=False,
    )

    # 2. Melhor Tempo (Primary Y)
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["melhor_tempo"],
            mode="lines+markers",
            name="Melhor Tempo (s)",
            line=dict(color="#2E7D32", width=2, dash="dash"),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Melhor Tempo: %{y:.2f}s<extra></extra>",
        ),
        secondary_y=False,
    )

    # 3. Distância Média de Entrega (Secondary Y)
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=df["distancia_media_entrega"],
            mode="lines+markers",
            name="Distância Média",
            line=dict(color="#7B1FA2", width=2.5),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Distância Média: %{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.02,
            font=dict(size=16),
        ),
        xaxis=dict(
            title="Geração",
            gridcolor="#F0F0F0",
            dtick=1 if len(generations) <= 20 else None,
        ),
        yaxis=dict(
            title="Tempo de Operação (s)",
            gridcolor="#F0F0F0",
        ),
        yaxis2=dict(
            title="Distância Média",
            gridcolor="#F0F0F0",
            showgrid=False,
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig


def build_logistics_performance_figure(
    execution_data: pd.DataFrame,
    title: str = "Evolução Operacional por Geração",
) -> go.Figure:
    """Build the operational evolution figure.

    Maintained for backwards-compatibility with previous placeholder signature.

    Args:
        execution_data: Standardized DataFrame compliant with the Data Contract.
        title: Title of the generated chart.

    Returns:
        go.Figure: Interactive Plotly figure.
    """
    return build_operational_evolution_figure(execution_data, title=title)
