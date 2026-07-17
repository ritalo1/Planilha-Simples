import streamlit as st

def render_header():
    st.markdown(
        """
        <div style='text-align:center;margin-bottom:20px;'>
            <h1 style='font-size:42px; font-weight:700;'>
                <span style='color:#9b5de5;'>[📊] Pocket</span>
                <span style='color:#f4a261;'>DBA</span>
            </h1>
            <p style='color:#BBBBBB; font-size:14px;'>
                Seu assistente de dados: ETL, SQL e IA — tudo no seu bolso.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    st.sidebar.markdown(
        "<h3 style='color:#9b5de5; font-size:18px;'>[⚙️] Navegação</h3>",
        unsafe_allow_html=True
    )

    pagina = st.sidebar.radio(
        "[📂] Escolha a página:",
        ["[📈] Dashboard", "[💻] Console SQL", "[🧾] Planilhas"]
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "<h4 style='color:#9b5de5; font-size:16px;'>[🎛] Modo PocketDBA</h4>",
        unsafe_allow_html=True
    )
    modo = st.sidebar.radio(
        "Modo de uso:",
        ["Simples", "Completo"],
        index=0
    )
    st.session_state.modo_pocketdba = modo

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "<h4 style='color:#9b5de5; font-size:16px;'>[🤖] Assistente IA</h4>",
        unsafe_allow_html=True
    )
    ia_on = st.sidebar.checkbox("Ativar assistente PocketDBA (Gemini)", value=False)
    st.session_state.ia_on = ia_on

    st.sidebar.markdown("---")

    paleta = {
        "Roxo Pocket": "#9b5de5",
        "Laranja DBA": "#f4a261",
        "Azul": "#2196F3",
        "Cinza": "#BDBDBD"
    }

    nome_cor = st.sidebar.selectbox("Cor principal dos elementos", list(paleta.keys()))
    st.session_state.cor_grafico = paleta[nome_cor]

    return pagina
