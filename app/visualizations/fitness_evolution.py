"""Fitness evolution visualizations for training analysis.

Provides Plotly figures illustrating fitness convergence, best/average/worst
fitness curves, and standard deviation intervals per generation according to
the canonical Data Contract.
"""

from typing import Any
import pandas as pd
import plotly.graph_objects as go


def build_fitness_evolution_figure(
    training_data: pd.DataFrame,
    title: str = "Evolução do Fitness por Geração",
) -> go.Figure:
    """Build a line chart showing fitness evolution per generation.

    Plots Best Fitness, Average Fitness, and Worst Fitness across generations,
    with a shaded confidence area representing the Standard Deviation
    (Average Fitness ± Std Dev) to demonstrate population convergence.

    Args:
        training_data: Standardized DataFrame compliant with the Data Contract.
        title: Title of the generated chart.

    Returns:
        go.Figure: Interactive Plotly figure.
    """
    fig = go.Figure()

    if training_data is None or training_data.empty:
        fig.add_annotation(
            text="Nenhum dado de treinamento disponível para visualização.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(
            title=title,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template="plotly_white",
        )
        return fig

    # Ensure required columns exist with defaults if missing
    df = training_data.copy()
    for col in ["geracao", "fit_melhor", "fit_medio", "fit_pior", "fit_std"]:
        if col not in df.columns:
            df[col] = 0.0 if col != "geracao" else range(1, len(df) + 1)

    generations = df["geracao"]
    fit_medio = df["fit_medio"]
    fit_std = df["fit_std"]
    fit_melhor = df["fit_melhor"]
    fit_pior = df["fit_pior"]

    has_std = fit_std.sum() > 0 or (fit_std > 0).any()

    # 1. Shaded area for Standard Deviation (Fit Médio ± Std)
    if has_std:
        upper_bound = fit_medio + fit_std
        lower_bound = fit_medio - fit_std

        # Trace for upper bound
        fig.add_trace(
            go.Scatter(
                x=generations,
                y=upper_bound,
                mode="lines",
                line=dict(width=0),
                hoverinfo="skip",
                showlegend=False,
                name="Desvio Superior",
            )
        )

        # Trace for lower bound with fill to upper bound
        fig.add_trace(
            go.Scatter(
                x=generations,
                y=lower_bound,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(33, 150, 243, 0.18)",  # Soft translucent blue
                name="Desvio Padrão (±1 std)",
                hoverinfo="skip",
                showlegend=True,
            )
        )

    # 2. Pior Fitness
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=fit_pior,
            mode="lines+markers",
            name="Pior Fitness",
            line=dict(color="#E53935", width=2, dash="dot"),
            marker=dict(size=4),
            hovertemplate="Geração %{x}<br>Pior: %{y:.2f}<extra></extra>",
        )
    )

    # 3. Fitness Médio
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=fit_medio,
            mode="lines+markers",
            name="Fitness Médio",
            line=dict(color="#1E88E5", width=2.5),
            marker=dict(size=5),
            hovertemplate="Geração %{x}<br>Médio: %{y:.2f}<extra></extra>",
        )
    )

    # 4. Melhor Fitness
    fig.add_trace(
        go.Scatter(
            x=generations,
            y=fit_melhor,
            mode="lines+markers",
            name="Melhor Fitness",
            line=dict(color="#43A047", width=2.5),
            marker=dict(size=6),
            hovertemplate="Geração %{x}<br>Melhor: %{y:.2f}<extra></extra>",
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
            title="Pontuação de Fitness",
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


def build_mutation_parameters_figure(
    training_data: pd.DataFrame,
    title: str = "Dinâmica de Mutação por Geração",
) -> go.Figure:
    """Build a chart tracking mutation rate and mutation strength across generations.

    Args:
        training_data: Standardized DataFrame compliant with the Data Contract.
        title: Title of the generated chart.

    Returns:
        go.Figure: Interactive Plotly figure.
    """
    fig = go.Figure()

    if training_data is None or training_data.empty:
        fig.add_annotation(
            text="Nenhum dado disponível para dinâmica de mutação.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(title=title, template="plotly_white")
        return fig

    df = training_data.copy()
    generations = df["geracao"] if "geracao" in df.columns else range(1, len(df) + 1)
    taxa = df["taxa_mutacao_atual"] if "taxa_mutacao_atual" in df.columns else [0.0] * len(df)
    forca = df["forca_mutacao_atual"] if "forca_mutacao_atual" in df.columns else [0.0] * len(df)

    fig.add_trace(
        go.Scatter(
            x=generations,
            y=taxa,
            mode="lines+markers",
            name="Taxa de Mutação",
            line=dict(color="#8E24AA", width=2),
            hovertemplate="Geração %{x}<br>Taxa: %{y:.4f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=generations,
            y=forca,
            mode="lines+markers",
            name="Força de Mutação",
            line=dict(color="#FB8C00", width=2, dash="dash"),
            hovertemplate="Geração %{x}<br>Força: %{y:.4f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.02, font=dict(size=16)),
        xaxis=dict(title="Geração", gridcolor="#F0F0F0"),
        yaxis=dict(title="Valor do Hiperparâmetro", gridcolor="#F0F0F0"),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig
