"""Streamlit entry point for the analytical dashboard."""

import streamlit as st

st.set_page_config(page_title="Dashboard Analítico", layout="wide")

st.title("Dashboard Analítico")
st.write(
    "Camada analítica do projeto de neuroevolução para comparar resultados "
    "de treinamento e execuções da simulação logística 3D."
)

st.info(
    "Implementação inicial: a estrutura, os contratos de dados e os módulos base "
    "foram preparados para evolução incremental."
)
