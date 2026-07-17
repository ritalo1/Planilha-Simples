import streamlit as st

def render_header():
    st.markdown(
        """
        <div style='text-align:center;margin-bottom:20px;'>
            <h1 style='font-size:42px;'>
                <span style='color:#9b5de5;'>📊 Pocket</span>
                <span style='color:#f4a261;'>DBA</span>
            </h1>
            <p style='color:#BBBBBB; font-size:16px;'>
                Seu assistente de dados: Dashboard, ETL, SQL e IA — tudo no seu bolso.
            </p>
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

    st.sidebar.markdown("### 🎛 Modo PocketDBA")
    modo = st.sidebar.radio(
        "Modo de uso:",
        ["Simples", "Completo"],
        index=0
    )
    st.session_state.modo_pocketdba = modo

    st.sidebar.markdown("---")

    st.sidebar.markdown("### 🤖 Assistente IA")
    ia_on = st.sidebar.checkbox("Ativar assistente PocketDBA (Gemini)", value=False)
    st.session_state.ia_on = ia_on

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
