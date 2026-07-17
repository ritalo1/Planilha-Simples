import streamlit as st

def render_header():
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:2rem;'>
            <h1 style='font-size:3rem; font-weight:800; letter-spacing:-1px;'>
                <span style='color:#9b5de5;'>[📊] Pocket</span><span style='color:#f4a261;'>DBA</span>
            </h1>
            <p style='color:#BBBBBB; font-size:1.1rem; margin-top:-10px;'>
                Seu assistente de dados: ETL, SQL e IA — tudo no seu bolso.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    st.sidebar.markdown("### [⚙️] Navegação")

    # Tenta usar o componente moderno; se a versão do Streamlit for antiga, usa o rádio horizontal
    try:
        pagina = st.sidebar.segmented_control(
            "Escolha a página:",
            ["[📈] Dashboard", "[💻] Console SQL", "[🧾] Planilhas"],
            default="[🧾] Planilhas",
            label_visibility="collapsed"
        )
    except AttributeError:
        pagina = st.sidebar.radio(
            "Escolha a página:",
            ["[📈] Dashboard", "[💻] Console SQL", "[🧾] Planilhas"]
        )

    st.sidebar.markdown("---")

    st.sidebar.markdown("#### [🎛] Modo PocketDBA")
    try:
        modo = st.sidebar.pills(
            "Modo de uso:",
            ["Simples", "Completo"],
            default="Simples",
            label_visibility="collapsed"
        )
    except AttributeError:
        modo = st.sidebar.radio("Modo de uso:", ["Simples", "Completo"], horizontal=True, label_visibility="collapsed")
    
    st.session_state.modo_pocketdba = modo

    st.sidebar.markdown("---")

    st.sidebar.markdown("#### [🤖] Assistente IA")
    # Caixinha em volta da ativação da IA para dar destaque
    with st.sidebar.container(border=True):
        ia_on = st.checkbox("Ativar PocketDBA (Gemini)", value=False)
        st.session_state.ia_on = ia_on

    st.sidebar.markdown("---")

    paleta = {
        "Roxo Pocket": "#9b5de5",
        "Laranja DBA": "#f4a261",
        "Azul": "#2196F3",
        "Verde": "#4CAF50"
    }

    with st.sidebar.container(border=True):
        nome_cor = st.selectbox("Cor secundária (Gráficos)", list(paleta.keys()))
        st.session_state.cor_grafico = paleta[nome_cor]

    return pagina
