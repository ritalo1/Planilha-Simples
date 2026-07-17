import streamlit as st
import pandas as pd

from modules.interface import render_header, render_sidebar
from modules.dashboard import render_dashboard
from modules.console_sql import render_console_sql
from modules.planilhas import render_planilhas
from modules.utils import aplicar_filtros
from modules.ia_sql import chat_dba

# Estado inicial
if "planilhas" not in st.session_state:
    st.session_state.planilhas = {"Principal": pd.DataFrame(columns=["Descrição", "Categoria", "Data", "Valor", "Observações"])}

if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = ""

# Header
render_header()

# Sidebar
pagina = render_sidebar()
cor = st.session_state.get("cor_grafico", "#4CAF50")

# Assistente IA flutuante (apenas UI simples)
if st.session_state.get("ia_on", False):
    with st.container():
        st.markdown(
            """
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 320px;
                padding: 15px;
                background: #ffffffee;
                border-radius: 12px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                z-index: 999;
            ">
            """,
            unsafe_allow_html=True
        )

        st.markdown("**🤖 PocketDBA — Assistente IA**")
        msg = st.text_area("Pergunte sobre seus dados, SQL ou boas práticas:", key="ia_msg")

        if st.button("Enviar para PocketDBA", key="ia_send"):
            st.session_state.historico_chat += f"\nUsuário: {msg}"
            resposta = chat_dba(msg, st.session_state.historico_chat)
            st.session_state.historico_chat += f"\nPocketDBA: {resposta}"
            st.write(resposta)

        st.markdown("</div>", unsafe_allow_html=True)

# Página selecionada
nome_planilha = "Principal"
df = st.session_state.planilhas[nome_planilha]

if pagina == "Dashboard":
    st.markdown(
        "<p style='color:#BBBBBB;'>Visão geral dos seus dados: totais, frequências e gráficos por categoria.</p>",
        unsafe_allow_html=True
    )

    st.markdown("### 🎚 Filtros")
    filtros_on = st.checkbox("Ativar filtros", value=True)
    categorias_sel = st.multiselect("Categorias", df["Categoria"].unique().tolist())
    data_ini = st.date_input("Data inicial")
    data_fim = st.date_input("Data final")
    vmin = st.number_input("Valor mínimo", value=0.0)
    vmax = st.number_input("Valor máximo", value=10000.0)
    texto = st.text_input("Buscar na descrição")

    df_filtrado = aplicar_filtros(df, filtros_on, categorias_sel, data_ini, data_fim, vmin, vmax, texto)

    meta_orcamento = st.number_input("Meta de orçamento (opcional)", value=0.0)
    mostrar_kpis = st.checkbox("Mostrar KPIs", value=True)
    mostrar_graficos = st.checkbox("Mostrar gráficos", value=True)

    coluna_kpi = "Categoria"
    coluna_graf = "Categoria"

    render_dashboard(
        df,
        nome_planilha,
        filtros_on,
        meta_orcamento,
        mostrar_kpis,
        coluna_kpi,
        coluna_graf,
        destacar_outliers=False,
        mostrar_graficos=mostrar_graficos,
        grafico_donut_on=True,
        grafico_barras_on=True,
        grafico_linha_on=True,
        grafico_histograma_on=False,
        grafico_boxplot_on=False,
        df_filtrado=df_filtrado,
        cor=cor
    )

elif pagina == "Console SQL":
    st.markdown(
        "<p style='color:#BBBBBB;'>Execute consultas SQL sobre seus dados, com correção automática de sintaxe.</p>",
        unsafe_allow_html=True
    )
    render_console_sql(df, nome_planilha)

elif pagina == "Planilhas":
    st.markdown(
        "<p style='color:#BBBBBB;'>Edite, limpe, transforme e exporte suas planilhas com ferramentas simples e rápidas.</p>",
        unsafe_allow_html=True
    )
    render_planilhas(df, nome_planilha)
