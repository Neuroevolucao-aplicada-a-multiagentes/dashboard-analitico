"""Population dynamics and checkpoints page."""

from pathlib import Path
import streamlit as st
import pandas as pd

from app.data.data_manager import get_data_manager
from app.visualizations.fitness_evolution import build_mutation_parameters_figure

st.set_page_config(page_title="População | Dashboard Analítico", layout="wide")

st.title("🧬 Análise Populacional & Checkpoints")
st.markdown(
    "Inspeção de dinâmica populacional, hiperparâmetros de mutação e registros de checkpoints geracionais."
)

st.markdown("---")

# --- AVISO ARQUITETURAL IMPORTANTE ---
st.info(
    "ℹ️ **Aviso Arquitetural (Fases Futuras)**: "
    "A análise microscópica de genomas individuais e morfologia de redes neurais consumirá artefatos de "
    "`core.checkpoint` em fases futuras. De acordo com as diretrizes do projeto (`AGENTS.md`), "
    "consultas diretas e irrestritas à tabela `core.individual` são expressamente evitadas para "
    "preservar a integridade de memória e desempenho de rede."
)

manager = get_data_manager()

st.sidebar.header("⚙️ Origem dos Dados")
source_option = st.sidebar.radio("Fonte:", options=["Local (CSV)", "Supabase"], index=0)

training_df: pd.DataFrame | None = None

if source_option == "Local (CSV)":
    local_dir = Path(manager.config.local_results_path)
    csv_files = []
    if local_dir.is_dir():
        csv_files = list(local_dir.glob("*.csv")) + list(local_dir.glob("*/*.csv"))
    data_dir = Path("data")
    if data_dir.is_dir():
        for f in data_dir.glob("**/*.csv"):
            if f not in csv_files:
                csv_files.append(f)

    file_options = {str(f): f for f in csv_files}
    if file_options:
        chosen_file = st.sidebar.selectbox("Selecione o arquivo CSV:", list(file_options.keys()), format_func=lambda x: Path(x).name)
        try:
            training_df = manager.get_run_metrics(file_options[chosen_file], source="local")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")
    else:
        st.sidebar.info("Nenhum CSV disponível localmente.")

else:
    if manager.supabase_client is not None:
        try:
            experiments = manager.list_experiments()
            if not experiments.empty and "id" in experiments.columns:
                exp_map = {
                    f"{row.get('name', 'Exp')} ({str(row['id'])[:8]}...)": str(row["id"])
                    for _, row in experiments.iterrows()
                }
                chosen_exp = st.sidebar.selectbox("Experimento:", list(exp_map.keys()))
                runs = manager.list_runs(experiment_id=exp_map[chosen_exp])
                if not runs.empty and "id" in runs.columns:
                    run_map = {
                        f"Run {str(row['id'])[:8]}": str(row["id"])
                        for _, row in runs.iterrows()
                    }
                    chosen_run = st.sidebar.selectbox("Run:", list(run_map.keys()))
                    chosen_run_id = run_map[chosen_run]

                    training_df = manager.get_run_metrics(chosen_run_id, source="supabase")

                    st.subheader("💾 Checkpoints Registrados na Run")
                    checkpoints_df = manager.list_checkpoints(run_id=chosen_run_id)
                    if not checkpoints_df.empty:
                        st.dataframe(checkpoints_df, use_container_width=True)
                    else:
                        st.write("Nenhum checkpoint salvo encontrado para esta execução.")
        except Exception as e:
            st.error(f"Erro ao consultar Supabase: {e}")
    else:
        st.warning("Supabase não configurado. Ative credenciais no `.env` para consultar checkpoints.")

# --- DINÂMICA DE MUTAÇÃO AGREGADA ---
if training_df is not None and not training_df.empty:
    st.subheader("🧬 Dinâmica dos Hiperparâmetros Genéticos")
    st.markdown(
        "Acompanhamento da taxa de mutação e da força de perturbação aplicadas à população "
        "ao longo das gerações."
    )

    fig_mutation = build_mutation_parameters_figure(
        training_df,
        title="Evolução de Taxa e Força de Mutação",
    )
    st.plotly_chart(fig_mutation, use_container_width=True)
else:
    st.info("Carregue uma execução na barra lateral para visualizar as dinâmicas populacionais agregadas.")
