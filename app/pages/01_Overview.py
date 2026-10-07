"""Overview page presenting architectural summary and database status."""

import streamlit as st
import pandas as pd

from app.data.config import load_data_config
from app.data.data_manager import get_data_manager

st.set_page_config(page_title="Overview | Dashboard Analítico", layout="wide")

st.title("🏛️ Visão Geral & Arquitetura")
st.markdown(
    "Resumo executivo da arquitetura do ecossistema de neuroevolução e "
    "status dos serviços de dados integrados."
)

st.markdown("---")

# --- SEÇÃO 1: STATUS DO BANCO DE DADOS (SUPABASE) ---
st.subheader("🔌 Status do Banco de Dados & Conexão")

config = load_data_config()
manager = get_data_manager()

col_status, col_exp, col_runs, col_mode = st.columns(4)

has_credentials = bool(config.supabase_url and config.supabase_anon_key)

if not has_credentials:
    with col_status:
        st.metric(label="Status do Supabase", value="Local / Offline", delta="Sem credenciais", delta_color="off")
    with col_exp:
        st.metric(label="Experimentos no Banco", value="N/A")
    with col_runs:
        st.metric(label="Runs no Banco", value="N/A")
    with col_mode:
        st.metric(label="Fonte Padrão", value="Local (CSV)")

    st.info(
        "ℹ️ **Modo Offline/Local ativo**: O arquivo `.env` não possui `SUPABASE_URL` e `SUPABASE_ANON_KEY` configurados. "
        "O dashboard continuará operando normalmente carregando dados locais a partir do diretório configurado (`data/samples`)."
    )
else:
    # Attempt light connectivity check
    try:
        experiments_df = manager.list_experiments()
        runs_df = manager.list_runs()
        exp_count = len(experiments_df) if isinstance(experiments_df, pd.DataFrame) else 0
        run_count = len(runs_df) if isinstance(runs_df, pd.DataFrame) else 0

        with col_status:
            st.metric(label="Status do Supabase", value="Online", delta="Conectado", delta_color="normal")
        with col_exp:
            st.metric(label="Experimentos", value=exp_count)
        with col_runs:
            st.metric(label="Runs Registradas", value=run_count)
        with col_mode:
            st.metric(label="Origem Habilitada", value="Híbrida (Supabase + Local)")

        url_masked = config.supabase_url.split("//")[-1].split(".")[0] + "..." if config.supabase_url else ""
        st.success(f"Conexão ativa com o projeto Supabase (`{url_masked}`). Schema `core` acessível.")

    except Exception as e:
        with col_status:
            st.metric(label="Status do Supabase", value="Erro de Conexão", delta="Indisponível", delta_color="inverse")
        with col_exp:
            st.metric(label="Experimentos", value="--")
        with col_runs:
            st.metric(label="Runs", value="--")
        with col_mode:
            st.metric(label="Fallback", value="Local (CSV)")

        st.warning(
            f"⚠️ As variáveis do Supabase estão configuradas, mas a conexão falhou: `{str(e)}`. "
            "O dashboard utilizará a carga local como fallback seguro."
        )

st.markdown("---")

# --- SEÇÃO 2: ARQUITETURA E FLUXO DE DADOS ---
st.subheader("📐 Arquitetura Desacoplada e Data Contract")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("""
### Pilares do Ecossistema
O projeto opera sobre **três repositórios independentes**, comunicando-se estritamente por dados persistidos:

1. **`neuroevolucao-armazem-fases`**
   - Treinamento neuroevolutivo 2D / NEAT dos robôs de armazém.
   - Otimização das redes neurais de navegação e coleta de caixas.
   - Persistência das métricas geracionais e checkpoints no schema `core` do Supabase.

2. **`godot-3d`**
   - Simulação 3D com física realista e telemetria de sensores.
   - Avaliação de agentes treinados sob interferências dinâmicas e colisões reais.
   - Registro de métricas logísticas (tempo de entrega, caixas entregues, trajetórias).

3. **`dashboard-analitico` (Esta camada)**
   - Plataforma analítica interativa construída em Streamlit + Plotly.
   - Consumo padronizado de dados via **Data Contract** e a fachada `DataManager`.
   - Comparação empírica entre o treinamento 2D e o comportamento físico 3D.
""")

with col_right:
    st.markdown("""
### Regras Críticas de Engenharia & Desempenho
- **Desacoplamento Rigoroso**: O dashboard **nunca** importa código-fonte dos repositórios irmãos, garantindo manutenibilidade e isolamento.
- **Proteção de Memória (`core.individual`)**: Consultas analíticas utilizam agregações em `core.generation` e `core.checkpoint`. Nunca são feitas consultas completas ou irrestritas à tabela `core.individual`.
- **Paridade Estrita**: Seja lendo arquivos CSV locais ou consultando o Supabase, a fachada `DataManager` padroniza tipos, nomes e ordenações das colunas canônicas.
- **Transparência Acadêmica**: Todas as visualizações contam com intervalos estatísticos (desvio padrão e médias) para análise robusta de convergência.
""")

st.markdown("---")

# --- SEÇÃO 3: GUIA DE NAVEGAÇÃO ---
st.subheader("🧭 Roteiro de Análise")

nav_c1, nav_c2, nav_c3 = st.columns(3)

with nav_c1:
    st.markdown("""
#### 📈 02. Training
- Visualização da evolução do fitness (Melhor, Médio e Pior).
- Área de desvio padrão (±1 std) demonstrando a estabilidade da convergência.
- Métricas instantâneas da última geração executada.
""")

with nav_c2:
    st.markdown("""
#### 🧬 03. Population
- Dinâmica dos hiperparâmetros genéticos (taxa e força de mutação).
- Inspecionamento dos checkpoints geracionais salvos.
- Monitoramento de diversidade da população.
""")

with nav_c3:
    st.markdown("""
#### 📦 04. Logistics & Mais
- Métricas operacionais do armazém (entregas, coletas e colisões).
- Taxas de eficiência temporal e física na simulação 3D.
- *(Previsto para a Fase D do roadmap).*
""")
