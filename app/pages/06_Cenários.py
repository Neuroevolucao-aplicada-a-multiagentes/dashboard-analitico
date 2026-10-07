"""Comparative analysis page for multiple neuroevolution runs."""

from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from app.analysis.comparative_analysis import (
    build_comparative_fitness_logistics_chart,
)
from app.data.data_manager import DataManager, get_data_manager


def _local_csv_files(manager: DataManager) -> list[Path]:
    """Return available local CSV files without duplicates."""
    candidates: list[Path] = []
    for directory in (Path(manager.config.local_results_path), Path("data")):
        if directory.is_dir():
            candidates.extend(directory.glob("*.csv"))
            candidates.extend(directory.glob("*/*.csv"))
    return list(dict.fromkeys(path for path in candidates if path.is_file()))


def _load_local_file(
    manager: DataManager,
    uploaded_file: UploadedFile | None,
    path: Path | None,
) -> pd.DataFrame | None:
    """Load an uploaded file or selected local file through the DataManager."""
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temporary_file:
            temporary_file.write(uploaded_file.getvalue())
            temporary_path = Path(temporary_file.name)
        try:
            return manager.get_run_metrics(temporary_path, source="local")
        finally:
            temporary_path.unlink(missing_ok=True)
    if path is not None:
        return manager.get_run_metrics(path, source="local")
    return None


def _load_slot(manager: DataManager, slot: int, experiments: pd.DataFrame) -> tuple[str, pd.DataFrame] | None:
    """Render and load one run-selection slot."""
    st.sidebar.subheader(f"Execução {slot}")
    source = st.sidebar.radio(
        "Fonte",
        options=("Local (CSV)", "Supabase"),
        key=f"scenario_source_{slot}",
        horizontal=True,
    )

    if source == "Local (CSV)":
        files = _local_csv_files(manager)
        file_map = {str(path): path for path in files}
        selected_path: Path | None = None
        if file_map:
            selected_key = st.sidebar.selectbox(
                "Arquivo CSV",
                options=list(file_map),
                format_func=lambda value: Path(value).name,
                key=f"scenario_file_{slot}",
            )
            selected_path = file_map[selected_key]
        uploaded_file = st.sidebar.file_uploader(
            "Ou envie um CSV",
            type=["csv"],
            key=f"scenario_upload_{slot}",
        )
        if not file_map and uploaded_file is None:
            st.sidebar.info("Nenhum CSV local encontrado.")
            return None
        try:
            data = _load_local_file(manager, uploaded_file, selected_path)
        except (OSError, ValueError) as error:
            st.sidebar.error(f"Erro ao carregar a fonte local: {error}")
            return None
        if data is None or data.empty:
            return None
        label = uploaded_file.name if uploaded_file is not None else Path(selected_path).stem
        return str(label), data

    if manager.supabase_client is None:
        st.sidebar.warning("Supabase não está configurado.")
        return None
    if experiments.empty or "id" not in experiments.columns:
        st.sidebar.info("Nenhum experimento encontrado no Supabase.")
        return None

    experiment_map = {
        f"{row.get('name', 'Sem nome')} ({str(row['id'])[:8]}...)": str(row["id"])
        for _, row in experiments.iterrows()
    }
    experiment_label = st.sidebar.selectbox(
        "Experimento",
        options=list(experiment_map),
        key=f"scenario_experiment_{slot}",
    )
    runs = manager.list_runs(experiment_id=experiment_map[experiment_label])
    if runs.empty or "id" not in runs.columns:
        st.sidebar.info("Nenhuma execução encontrada para este experimento.")
        return None
    run_map = {
        f"Execução {str(row['id'])[:8]} ({row.get('status', 'N/A')})": str(row["id"])
        for _, row in runs.iterrows()
    }
    run_label = st.sidebar.selectbox(
        "Execução",
        options=list(run_map),
        key=f"scenario_run_{slot}",
    )
    if not st.sidebar.button("Carregar execução", key=f"scenario_load_{slot}"):
        return None
    try:
        data = manager.get_run_metrics(run_map[run_label], source="supabase")
    except (RuntimeError, ValueError) as error:
        st.sidebar.error(f"Erro ao carregar a execução: {error}")
        return None
    return run_label, data


st.set_page_config(page_title="Cenários | Dashboard Analítico", layout="wide")
st.title("🔬 Análise Comparativa de Cenários")
st.markdown(
    "Compare a evolução do fitness médio e da taxa de entrega de duas ou mais execuções "
    "usando o mesmo eixo de gerações."
)
st.sidebar.header("⚙️ Fontes para comparação")

manager = get_data_manager()
try:
    experiments_df = manager.list_experiments() if manager.supabase_client is not None else pd.DataFrame()
except (RuntimeError, ValueError):
    experiments_df = pd.DataFrame()

comparative_runs: dict[str, pd.DataFrame] = {}
for slot in (1, 2):
    selected_run = _load_slot(manager, slot, experiments_df)
    if selected_run is not None:
        label, data = selected_run
        comparative_runs[f"Execução {slot}: {label}"] = data

if len(comparative_runs) < 2:
    st.info("Selecione e carregue pelo menos duas execuções para visualizar a comparação.")
else:
    st.caption(f"{len(comparative_runs)} execuções carregadas para comparação.")
    figure = build_comparative_fitness_logistics_chart(comparative_runs)
    st.plotly_chart(figure, use_container_width=True)
