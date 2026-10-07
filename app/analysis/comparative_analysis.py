"""Comparative charts for standardized run metrics."""

from collections.abc import Mapping

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_comparative_fitness_logistics_chart(
    dict_of_dfs: Mapping[str, pd.DataFrame],
) -> go.Figure:
    """Build a two-panel comparison of fitness and delivery rate by generation.

    The input tables are expected to follow the canonical ``RunMetrics`` contract.
    Missing metric columns are treated as zero so the chart remains usable with
    partially populated local files.
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=("Fitness Médio", "Taxa de Entrega"),
    )

    colors = (
        "#1E88E5",
        "#43A047",
        "#FB8C00",
        "#8E24AA",
        "#E53935",
        "#00897B",
    )

    for index, (run_name, run_df) in enumerate(dict_of_dfs.items()):
        if run_df is None or run_df.empty:
            continue

        df = run_df.copy()
        generations = (
            df["geracao"]
            if "geracao" in df.columns
            else pd.Series(range(1, len(df) + 1), index=df.index)
        )
        fitness = (
            df["fit_medio"]
            if "fit_medio" in df.columns
            else pd.Series(0.0, index=df.index)
        )
        delivery_rate = (
            df["taxa_entrega"]
            if "taxa_entrega" in df.columns
            else pd.Series(0.0, index=df.index)
        )
        color = colors[index % len(colors)]

        fig.add_trace(
            go.Scatter(
                x=generations,
                y=fitness,
                mode="lines+markers",
                name=f"{run_name} — Fitness Médio",
                legendgroup=str(run_name),
                line=dict(color=color, width=2.5),
                marker=dict(size=5),
                hovertemplate=(
                    f"{run_name}<br>Geração %{{x}}"
                    "<br>Fitness Médio: %{y:.2f}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=generations,
                y=delivery_rate,
                mode="lines+markers",
                name=f"{run_name} — Taxa de Entrega",
                legendgroup=str(run_name),
                showlegend=False,
                line=dict(color=color, width=2.5),
                marker=dict(size=5),
                hovertemplate=(
                    f"{run_name}<br>Geração %{{x}}"
                    "<br>Taxa de Entrega: %{y:.1%}<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    if not fig.data:
        fig.add_annotation(
            text="Nenhuma run disponível para comparação.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )

    fig.update_yaxes(title_text="Fitness", row=1, col=1, gridcolor="#F0F0F0")
    fig.update_yaxes(title_text="Taxa", tickformat=".0%", row=2, col=1, gridcolor="#F0F0F0")
    fig.update_xaxes(title_text="Geração", row=2, col=1, gridcolor="#F0F0F0")
    fig.update_layout(
        title=dict(text="<b>Comparação entre Runs: Fitness e Logística</b>", x=0.02),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=50, r=40, t=90, b=45),
    )
    return fig
