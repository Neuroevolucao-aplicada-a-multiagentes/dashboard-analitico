"""Loader for static metrics CSV files."""

from pathlib import Path
from typing import Union
import pandas as pd

METRICS_INT_COLUMNS = [
    "geracao",
    "coletas",
    "entregas",
    "colisoes",
    "mortos",
]

METRICS_FLOAT_COLUMNS = [
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


def load_metrics_csv(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load, clean and validate a metrics CSV file from training runs.

    Args:
        file_path: Path to the CSV file.

    Returns:
        pd.DataFrame with cleaned, typed and sorted metrics.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If file is empty or missing essential columns.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de métricas não encontrado: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"O arquivo de métricas está vazio: {path}")

    if df.empty:
        raise ValueError(f"O arquivo de métricas não contém dados: {path}")

    # Remove espaços em branco dos nomes das colunas
    df.columns = df.columns.str.strip()

    if "geracao" not in df.columns:
        raise ValueError("Coluna obrigatória 'geracao' não encontrada no arquivo.")

    # Converte tipos inteiros tratando nulos com 0
    for col in METRICS_INT_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Converte tipos float tratando nulos com 0.0
    for col in METRICS_FLOAT_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)

    # Ordena por geracao de forma crescente
    df = df.sort_values(by="geracao").reset_index(drop=True)

    return df
