"""Tests for sample/local metrics loader."""

import pytest
import pandas as pd
from app.data.sample_loader import load_metrics_csv


def test_load_metrics_csv_success(tmp_path):
    csv_content = (
        "geracao,fit_medio,fit_melhor,fit_pior,fit_std,coletas,entregas,colisoes,mortos,taxa_coleta,taxa_entrega,melhor_tempo,tempo_medio_entrega,distancia_media_entrega,taxa_mutacao_atual,forca_mutacao_atual,tempo_real_geracao_seg\n"
        "2,100.5,200.0,50.0,15.2,5,3,1,0,0.5,0.3,12.5,14.2,500.0,0.1,0.2,1.2\n"
        "1,80.0,150.0,40.0,10.0,4,2,0,0,0.4,0.2,15.0,18.0,600.0,0.1,0.2,1.1\n"
    )
    test_file = tmp_path / "metricas.csv"
    test_file.write_text(csv_content, encoding="utf-8")

    df = load_metrics_csv(test_file)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    # Ensure sorted by geracao
    assert df["geracao"].tolist() == [1, 2]
    assert df["fit_melhor"].iloc[0] == 150.0
    assert df["coletas"].dtype.kind in ("i", "u")
    assert df["fit_medio"].dtype.kind == "f"


def test_load_metrics_csv_handles_nulls(tmp_path):
    csv_content = (
        "geracao,fit_medio,fit_melhor,fit_pior,fit_std,coletas,entregas,colisoes,mortos,taxa_coleta,taxa_entrega,melhor_tempo,tempo_medio_entrega,distancia_media_entrega,taxa_mutacao_atual,forca_mutacao_atual,tempo_real_geracao_seg\n"
        "1,80.0,150.0,,NaN,4,,0,0,0.4,0.2,15.0,18.0,600.0,0.1,0.2,1.1\n"
    )
    test_file = tmp_path / "metricas_nulls.csv"
    test_file.write_text(csv_content, encoding="utf-8")

    df = load_metrics_csv(test_file)

    assert df["fit_pior"].iloc[0] == 0.0
    assert df["fit_std"].iloc[0] == 0.0
    assert df["entregas"].iloc[0] == 0


def test_load_metrics_csv_missing_file():
    with pytest.raises(FileNotFoundError):
        load_metrics_csv("caminho_inexistente_12345.csv")


def test_load_metrics_csv_empty_file(tmp_path):
    test_file = tmp_path / "empty.csv"
    test_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        load_metrics_csv(test_file)
