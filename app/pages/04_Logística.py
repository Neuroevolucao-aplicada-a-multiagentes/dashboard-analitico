"""Logistics performance page for warehouse operational analysis.

Allows selecting data sources (Local CSV vs Supabase), inspecting key latest-generation
logistics KPIs (taxa de coleta, taxa de entrega, colisões, melhor tempo), and visualizing
operational evolution and efficiency curves.
"""

from pathlib import Path
import tempfile
import streamlit as st
import pandas as pd

from app.data.data_manager import get_data_manager
from app.analysis.execution_metrics import summarize_logistics_metrics
from app.visualizations.logistics_performance import (
    build_operational_evolution_figure,
    build_efficiency_time_figure,
)

st.set_page_config(page_title="Logística | Dashboard Analítico", layout="wide")

st.title("📦 Desempenho Logístico & Operacional")
st.markdown(
    "Acompanhe a eficiência das operações no armazém simulado: "
    "taxas de coleta e entrega, colisões, tempos de rota e distâncias médias."
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

logistics_df: pd.DataFrame | None = None
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
        help="Envie um arquivo CSV contendo o histórico de métricas de execução.",
    )

    if uploaded_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = Path(tmp.name)
            logistics_df = manager.get_run_metrics(tmp_path, source="local")
            data_source_label = f"Arquivo enviado: {uploaded_file.name}"
        except Exception as e:
            st.error(f"Erro ao ler arquivo enviado: {e}")
    elif selected_file_path is not None:
        try:
            logistics_df = manager.get_run_metrics(selected_file_path, source="local")
            data_source_label = f"Arquivo local: {selected_file_path.name}"
        except Exception as e:
            st.error(f"Erro ao carregar {selected_file_path}: {e}")
    else:
        st.sidebar.info("Nenhum arquivo CSV encontrado em `data/`.")
        # Provide sample demo loader button for testing/development
        if st.sidebar.button("Carregar Dados de Demonstração"):
            demo_data = {
                "geracao": list(range(1, 26)),
                "coletas": [int(10 + i * 2.5) for i in range(1, 26)],
                "entregas": [int(5 + i * 2.1) for i in range(1, 26)],
                "colisoes": [max(0, int(15 - 0.5 * i)) for i in range(1, 26)],
                "mortos": [max(0, int(4 - 0.15 * i)) for i in range(1, 26)],
                "taxa_coleta": [min(1.0, 0.40 + 0.022 * i) for i in range(1, 26)],
                "taxa_entrega": [min(1.0, 0.25 + 0.028 * i) for i in range(1, 26)],
                "melhor_tempo": [max(6.0, 25.0 - 0.7 * i) for i in range(1, 26)],
                "tempo_medio_entrega": [max(9.0, 32.0 - 0.85 * i) for i in range(1, 26)],
                "distancia_media_entrega": [max(30.0, 65.0 - 1.1 * i) for i in range(1, 26)],
                "fit_melhor": [45.0 + 12.0 * (i**0.6) for i in range(1, 26)],
                "fit_medio": [20.0 + 6.5 * (i**0.65) for i in range(1, 26)],
                "fit_pior": [5.0 + 1.2 * i for i in range(1, 26)],
                "fit_std": [max(2.0, 15.0 - 0.45 * i) for i in range(1, 26)],
                "taxa_mutacao_atual": [max(0.05, 0.25 - 0.007 * i) for i in range(1, 26)],
                "forca_mutacao_atual": [max(0.1, 0.4 - 0.01 * i) for i in range(1, 26)],
                "tempo_real_geracao_seg": [12.0 + 0.1 * i for i in range(1, 26)],
            }
            demo_df = pd.DataFrame(demo_data)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as tmp:
                demo_df.to_csv(tmp.name, index=False)
                tmp_path = Path(tmp.name)
            logistics_df = manager.get_run_metrics(tmp_path, source="local")
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
                        f"Execução {str(row['id'])[:8]} (Status: {row.get('status', 'N/A')})": str(row["id"])
                        for _, row in runs.iterrows()
                    }
                    chosen_run_label = st.sidebar.selectbox("Execução:", options=list(run_map.keys()))
                    chosen_run_id = run_map[chosen_run_label]

                    if st.sidebar.button("Carregar Métricas da Execução", type="primary"):
                        logistics_df = manager.get_run_metrics(chosen_run_id, source="supabase")
                        data_source_label = f"Execução Supabase: {chosen_run_id}"
                else:
                    st.sidebar.info("Nenhuma execução encontrada para este experimento.")
            else:
                st.sidebar.info("Nenhum experimento encontrado.")
                manual_run_id = st.sidebar.text_input("Ou digite o UUID da execução:")
                if manual_run_id and st.sidebar.button("Carregar por UUID"):
                    logistics_df = manager.get_run_metrics(manual_run_id.strip(), source="supabase")
                    data_source_label = f"Execução Supabase: {manual_run_id.strip()}"
        except Exception as e:
            st.error(f"Erro ao consultar Supabase: {e}")

# --- APRESENTAÇÃO DOS DADOS ---
if logistics_df is None or logistics_df.empty:
    st.info(
        "👋 **Nenhum conjunto de execução logística selecionado no momento.**\n\n"
        "Selecione um arquivo CSV local, faça o upload de um arquivo ou selecione uma execução "
        "do Supabase na barra lateral esquerda para visualizar o desempenho logístico."
    )
else:
    st.caption(f"📍 **Fonte ativa**: {data_source_label}")

    metrics = summarize_logistics_metrics(logistics_df)

    # --- MÉTRICAS CHAVE DA ÚLTIMA GERAÇÃO ---
    st.subheader(f"📊 Indicadores Logísticos — Geração {metrics['latest_generation']}")

    col1, col2, col3, col4, col5 = st.columns(5)

    def _format_pct(val: float) -> str:
        return f"{val:.1%}" if abs(val) <= 1.0 else f"{val:.1f}%"

    def _format_pct_delta(delta: float) -> str:
        return f"{delta:+.1%}" if abs(delta) <= 1.0 else f"{delta:+.1f}%"

    with col1:
        st.metric(
            label="Taxa de Coleta",
            value=_format_pct(metrics["latest_taxa_coleta"]),
            delta=_format_pct_delta(metrics["delta_taxa_coleta"]) if metrics["has_delta"] else None,
            help="Proporção de itens coletados com sucesso na última geração.",
        )

    with col2:
        st.metric(
            label="Taxa de Entrega",
            value=_format_pct(metrics["latest_taxa_entrega"]),
            delta=_format_pct_delta(metrics["delta_taxa_entrega"]) if metrics["has_delta"] else None,
            help="Proporção de itens entregues com sucesso nos pontos de descarga.",
        )

    with col3:
        st.metric(
            label="Colisões",
            value=f"{metrics['latest_colisoes']}",
            delta=f"{metrics['delta_colisoes']:+d}" if metrics["has_delta"] else None,
            delta_color="inverse",
            help=f"Colisões registradas na última geração. Total acumulado na execução: {metrics['total_colisoes']}.",
        )

    with col4:
        st.metric(
            label="Melhor Tempo",
            value=f"{metrics['latest_melhor_tempo']:.2f} s",
            delta=f"{metrics['delta_melhor_tempo']:+.2f} s" if metrics["has_delta"] else None,
            delta_color="inverse",
            help="Menor tempo registrado para completar ciclo operacional.",
        )

    with col5:
        st.metric(
            label="Tempo Médio",
            value=f"{metrics['latest_tempo_medio_entrega']:.2f} s",
            delta=f"{metrics['delta_tempo_medio_entrega']:+.2f} s" if metrics["has_delta"] else None,
            delta_color="inverse",
            help="Tempo médio gasto para realização das entregas.",
        )

    st.markdown("---")

    # --- GRÁFICOS PLOTLY ---
    st.subheader("🚚 Evolução Operacional")
    st.markdown(
        "Acompanhamento da contagem de coletas, entregas, colisões e mortes de agentes ao longo das gerações."
    )
    fig_operational = build_operational_evolution_figure(
        logistics_df,
        title=f"Evolução Operacional ({data_source_label})",
    )
    st.plotly_chart(fig_operational, use_container_width=True)

    st.subheader("⏱️ Eficiência e Tempo de Operação")
    st.markdown(
        "Comparação entre os tempos de entrega (tempo médio e melhor tempo no eixo esquerdo) "
        "e a distância média percorrida até a entrega (eixo direito)."
    )
    fig_efficiency = build_efficiency_time_figure(
        logistics_df,
        title=f"Eficiência e Tempo de Operação ({data_source_label})",
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)

    # --- TABELA DE DADOS ---
    with st.expander("📋 Exibir Tabela de Dados Padronizada (Data Contract)"):
        st.dataframe(logistics_df, use_container_width=True)
        csv_bytes = logistics_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Dados Padronizados (CSV)",
            data=csv_bytes,
            file_name="metricas_logistica.csv",
            mime="text/csv",
        )
