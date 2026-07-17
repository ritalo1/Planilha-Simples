import streamlit as st

def render_header():
    st.markdown(
        """
        <div style='text-align:center;margin-bottom:20px;'>
            <h1 style='color:#4CAF50;'>💸 Sistema de Gastos PRO</h1>
            <p style='color:#BBBBBB;'>Dashboard, ETL e Console SQL — tudo em um só lugar.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    st.sidebar.markdown("## ⚙️ Navegação")

    pagina = st.sidebar.radio(
        "Escolha a página:",
        ["Dashboard", "Console SQL", "Planilhas"]
    )

    st.sidebar.markdown("---")

    paleta = {
        "Verde": "#4CAF50",
        "Verde escuro": "#2E7D32",
        "Azul": "#2196F3",
        "Azul claro": "#64B5F6",
        "Roxo": "#9C27B0",
        "Rosa": "#E91E63",
        "Laranja": "#FB8C00",
        "Cinza": "#BDBDBD"
    }

    nome_cor = st.sidebar.selectbox("Cor principal dos gráficos", list(paleta.keys()))
    st.session_state.cor_grafico = paleta[nome_cor]

    return pagina
