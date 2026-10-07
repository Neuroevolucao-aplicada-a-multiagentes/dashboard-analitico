"""Training analysis page for neuroevolution runs.

Allows selecting data sources (Local CSV vs Supabase), inspecting key latest-generation
metrics, and visualizing fitness curves with standard deviation convergence bounds.
"""

from pathlib import Path
import tempfile
import streamlit as st
import pandas as pd

from app.data.data_manager import get_data_manager
from app.analysis.training_metrics import summarize_training_metrics
from app.visualizations.fitness_evolution import build_fitness_evolution_figure

st.set_page_config(page_title="Treinamento | Dashboard Analítico", layout="wide")

st.title("📈 Análise de Treinamento e Convergência")
st.markdown(
    "Acompanhe a curva de aprendizado da população neuroevolutiva através da "
    "evolução do fitness (Melhor, Médio e Pior) com limites de desvio padrão."
)

st.markdown("---")

manager = get_data_manager()

# --- SIDEBAR: SELEÇÃO DA FONTE DE DADOS ---
st.sidebar.header("⚙️ Configurações da Fonte de Dados")
source_option = st.sidebar.radio(
    "Origem dos Dados:",
    options=["Local (CSV)", "Supabase"],
    index=0,
    help="Escolha se deseja analisar execuções de arquivos CSV locais ou do banco de dados Supabase.",
)

training_df: pd.DataFrame | None = None
data_source_label = ""

if source_option == "Local (CSV)":
    st.sidebar.subheader("Arquivos Locais")
    local_dir = Path(manager.config.local_results_path)
    csv_files = []
    if local_dir.is_dir():
        csv_files = list(local_dir.glob("*.csv")) + list(local_dir.glob("*/*.csv"))

    # Also search 'data' folder
    data_dir = Path("data")
    if data_dir.is_dir():
        for f in data_dir.glob("**/*.csv"):
            if f not in csv_files:
                csv_files.append(f)

    file_options = {str(f): f for f in csv_files}

    selected_file_path = None
    if file_options:
        chosen_key = st.sidebar.selectbox(
            "Selecione um arquivo CSV:",
            options=list(file_options.keys()),
            format_func=lambda x: Path(x).name,
        )
        selected_file_path = file_options[chosen_key]

    # File uploader option
    uploaded_file = st.sidebar.file_uploader(
        "Ou faça upload de arquivo CSV:",
        type=["csv"],
        help="Envie um arquivo CSV contendo o histórico de métricas de treinamento.",
    )

    if uploaded_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = Path(tmp.name)
            training_df = manager.get_run_metrics(tmp_path, source="local")
            data_source_label = f"Arquivo enviado: {uploaded_file.name}"
        except Exception as e:
            st.error(f"Erro ao ler arquivo enviado: {e}")
    elif selected_file_path is not None:
        try:
            training_df = manager.get_run_metrics(selected_file_path, source="local")
            data_source_label = f"Arquivo local: {selected_file_path.name}"
        except Exception as e:
            st.error(f"Erro ao carregar {selected_file_path}: {e}")
    else:
        st.sidebar.info("Nenhum arquivo CSV encontrado em `data/`.")
        # Provide sample demo loader button for testing/development
        if st.sidebar.button("Carregar Dados de Demonstração (Demo)"):
            demo_data = {
                "geracao": list(range(1, 26)),
                "fit_melhor": [
                    45.0 + 12.0 * (i**0.6) + (i % 3) * 1.5 for i in range(1, 26)
                ],
                "fit_medio": [
                    20.0 + 6.5 * (i**0.65) - (i % 2) * 1.0 for i in range(1, 26)
                ],
                "fit_pior": [
                    5.0 + 1.2 * i for i in range(1, 26)
                ],
                "fit_std": [
                    max(2.0, 15.0 - 0.45 * i) for i in range(1, 26)
                ],
                "coletas": [int(10 + i * 2.5) for i in range(1, 26)],
                "entregas": [int(5 + i * 2.1) for i in range(1, 26)],
                "colisoes": [max(0, int(15 - 0.5 * i)) for i in range(1, 26)],
                "mortos": [max(0, int(4 - 0.15 * i)) for i in range(1, 26)],
                "taxa_mutacao_atual": [max(0.05, 0.25 - 0.007 * i) for i in range(1, 26)],
                "forca_mutacao_atual": [max(0.1, 0.4 - 0.01 * i) for i in range(1, 26)],
            }
            demo_df = pd.DataFrame(demo_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as tmp:
                demo_df.to_csv(tmp.name, index=False)
                tmp_path = Path(tmp.name)
            training_df = manager.get_run_metrics(tmp_path, source="local")
            data_source_label = "Conjunto de Demonstração (Sintético)"

else:
    # SUPABASE SOURCE
    st.sidebar.subheader("Supabase (core)")
    if manager.supabase_client is None:
        st.error(
            "⚠️ Cliente Supabase não configurado. Por favor, configure `SUPABASE_URL` e "
            "`SUPABASE_ANON_KEY` no arquivo `.env` para consultar o banco diretamente."
        )
    else:
        try:
            experiments = manager.list_experiments()
            if not experiments.empty and "id" in experiments.columns:
                exp_map = {
                    f"{row.get('name', 'Sem nome')} ({str(row['id'])[:8]}...)": str(row["id"])
                    for _, row in experiments.iterrows()
                }
                chosen_exp_name = st.sidebar.selectbox("Experimento:", options=list(exp_map.keys()))
                chosen_exp_id = exp_map[chosen_exp_name]

                runs = manager.list_runs(experiment_id=chosen_exp_id)
                if not runs.empty and "id" in runs.columns:
                    run_map = {
                        f"Run {str(row['id'])[:8]} (Status: {row.get('status', 'N/A')})": str(row["id"])
                        for _, row in runs.iterrows()
                    }
                    chosen_run_label = st.sidebar.selectbox("Execução (Run):", options=list(run_map.keys()))
                    chosen_run_id = run_map[chosen_run_label]

                    if st.sidebar.button("Carregar Métricas da Run", type="primary"):
                        training_df = manager.get_run_metrics(chosen_run_id, source="supabase")
                        data_source_label = f"Supabase Run: {chosen_run_id}"
                else:
                    st.sidebar.info("Nenhuma run encontrada para este experimento.")
            else:
                st.sidebar.info("Nenhum experimento encontrado.")
                manual_run_id = st.sidebar.text_input("Ou digite o UUID da Run:")
                if manual_run_id and st.sidebar.button("Carregar por UUID"):
                    training_df = manager.get_run_metrics(manual_run_id.strip(), source="supabase")
                    data_source_label = f"Supabase Run: {manual_run_id.strip()}"
        except Exception as e:
            st.error(f"Erro ao consultar Supabase: {e}")

# --- APRESENTAÇÃO DOS DADOS ---
if training_df is None or training_df.empty:
    st.info(
        "👋 **Nenhum conjunto de treinamento selecionado no momento.**\n\n"
        "Selecione um arquivo CSV local, faça o upload de um arquivo ou selecione uma execução "
        "do Supabase na barra lateral esquerda para visualizar a análise."
    )
else:
    st.caption(f"📍 **Fonte ativa**: {data_source_label}")

    metrics = summarize_training_metrics(training_df)

    # --- MÉTRICAS CHAVE DA ÚLTIMA GERAÇÃO ---
    st.subheader(f"📊 Métricas Chave — Geração {metrics['latest_generation']}")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Melhor Fitness",
            value=f"{metrics['latest_best_fitness']:.2f}",
            delta=f"{metrics['delta_best']:+.2f}" if metrics["total_generations"] > 1 else None,
            help="Maior pontuação de fitness alcançada na última geração.",
        )

    with col2:
        st.metric(
            label="Fitness Médio",
            value=f"{metrics['latest_avg_fitness']:.2f}",
            delta=f"{metrics['delta_avg']:+.2f}" if metrics["total_generations"] > 1 else None,
            help="Média do fitness de todos os indivíduos da última geração.",
        )

    with col3:
        st.metric(
            label="Desvio Padrão (±)",
            value=f"{metrics['latest_std_fitness']:.2f}",
            help="Desvio padrão populacional do fitness na última geração. Valores menores indicam convergência.",
        )

    with col4:
        st.metric(
            label="Pior Fitness",
            value=f"{metrics['latest_worst_fitness']:.2f}",
            help="Menor pontuação registrada na última geração.",
        )

    with col5:
        st.metric(
            label="Ganho Total de Fitness",
            value=f"{metrics['fitness_gain']:+.2f}",
            help="Evolução do melhor fitness da Geração 1 até a geração atual.",
        )

    st.markdown("---")

    # --- GRÁFICO DE EVOLUÇÃO DO FITNESS ---
    st.subheader("📉 Curvas de Evolução e Convergência do Fitness")
    st.markdown(
        "O gráfico exibe o progresso do melhor indivíduo, da média da população e do pior indivíduo. "
        "A área azul sombreada representa a faixa de **±1 Desvio Padrão** ao redor da média, "
        "destacando a variabilidade genética e a convergência populacional."
    )

    fig_fitness = build_fitness_evolution_figure(
        training_df,
        title=f"Evolução do Fitness ({data_source_label})",
    )
    st.plotly_chart(fig_fitness, use_container_width=True)

    # --- TABELA DE DADOS ---
    with st.expander("📋 Exibir Tabela de Dados Padronizada (Data Contract)"):
        st.dataframe(training_df, use_container_width=True)
        csv_bytes = training_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Dados Padronizados (CSV)",
            data=csv_bytes,
            file_name="metricas_treinamento.csv",
            mime="text/csv",
        )
