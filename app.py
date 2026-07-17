import streamlit as st
import pandas as pd

from modules.interface import render_header, render_sidebar
from modules.planilhas import render_planilhas
from modules.console_sql import render_console_sql
from modules.dashboard import render_dashboard
from modules.utils import aplicar_filtros

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

MODELO = pd.DataFrame({
    "Descrição": pd.Series(dtype="str"),
    "Categoria": pd.Series(dtype="str"),
    "Data": pd.Series(dtype="datetime64[ns]"),
    "Valor": pd.Series(dtype="float"),
    "Observações": pd.Series(dtype="str")
})

st.set_page_config(
    page_title="Sistema de Gastos PRO",
    page_icon="💸",
    layout="wide"
)

if "planilhas" not in st.session_state:
    st.session_state.planilhas = {"Janeiro": MODELO.copy()}

if "cor_grafico" not in st.session_state:
    st.session_state.cor_grafico = "#4CAF50"

render_header()
pagina = render_sidebar()

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:
        df = st.session_state.planilhas[nome]

        if pagina == "Dashboard":
            # aqui depois a gente pluga o render_dashboard com os parâmetros certos
            st.write(f"Dashboard de {nome} (placeholder)")

        elif pagina == "Planilhas":
            render_planilhas(df, nome)

        elif pagina == "Console SQL":
            render_console_sql(df, nome)
