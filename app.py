import streamlit as st
import pandas as pd

from modules.interface import render_header, render_sidebar
from modules.console_sql import render_console_sql
from modules.planilhas import render_planilhas
from modules.utils import aplicar_filtros

# Estado inicial
if "planilhas" not in st.session_state:
    st.session_state.planilhas = {
        "Principal": pd.DataFrame(columns=["Descrição", "Categoria", "Data", "Valor", "Observações"])
    }

if "ia_log" not in st.session_state:
    st.session_state.ia_log = ""

# Header
render_header()

# Sidebar
pagina = render_sidebar()
cor = st.session_state.get("cor_grafico", "#9b5de5")

# Janela flutuante de IA (minimizada / expandida)
if "ia_expanded" not in st.session_state:
    st.session_state.ia_expanded = False

if st.session_state.get("ia_on", False):
    # Minimizada
    if not st.session_state.ia_expanded:
        st.markdown(
            """
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 8px 12px;
                background: #ffffffee;
                border-radius: 999px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                cursor: pointer;
                z-index: 999;
            "
            onclick="window.location.reload();">
                <span style="color:#9b5de5; font-weight:700;">[🤖]</span>
                <span style="color:#9b5de5; font-weight:700;">A</span><span style="color:#f4a261; font-weight:700;">I</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Hack simples: usuário toca, recarrega, e a gente pode alternar via botão se quiser depois
    else:
        st.markdown(
            """
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 320px;
                max-height: 260px;
                padding: 12px;
                background: #ffffffee;
                border-radius: 12px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                z-index: 999;
                overflow-y: auto;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="color:#9b5de5; font-weight:700;">[🤖] PocketDBA — IA</span>
                    <span style="cursor:pointer; color:#f4a261; font-weight:700;"
                          onclick="window.location.reload();">X</span>
                </div>
                <div style="font-size:13px; color:#555555;">
            """,
            unsafe_allow_html=True
        )
        st.markdown(st.session_state.ia_log or "Nenhuma interação registrada ainda.", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

# Página
nome_planilha = "Principal"
df = st.session_state.planilhas[nome_planilha]

if pagina == "[📈] Dashboard":
    st.markdown(
        "<p style='color:#BBBBBB; font-size:14px;'>Visão geral dos seus dados (gráficos serão adicionados depois).</p>",
        unsafe_allow_html=True
    )
    st.info("Dashboard em construção. Use Planilhas e Console SQL por enquanto.")

elif pagina == "[💻] Console SQL":
    render_console_sql(df, nome_planilha)

elif pagina == "[🧾] Planilhas":
    render_planilhas(df, nome_planilha)
