import streamlit as st

def render_home():
    # Hero Section (Cabeçalho de Impacto)
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 0 1rem 0;">
            <h1 style="font-size: 4rem; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 0;">
                <span style='color:#9b5de5;'>Pocket</span><span style='color:#f4a261;'>DBA</span>
            </h1>
            <h3 style="color: #FAFAFA; font-weight: 400; margin-top: 5px;">Seu ecossistema inteligente de dados</h3>
            <p style="font-size: 1.1rem; color: #BBBBBB; max-width: 700px; margin: 15px auto 30px auto; line-height: 1.6;">
                Um projeto independente voltado para <b>análise, tratamento, limpeza, formatação e condicionamento</b>. 
                Obtenha direcionamentos claros e insights automatizados a partir de dados importados ou preenchidos.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Seção de Funcionalidades (Cards com Borda)
    st.markdown("<h4 style='text-align: center; margin-bottom: 2rem;'>Como podemos ajudar hoje?</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("<h3 style='color:#9b5de5;'>🧹 Tratamento</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='font-size: 0.9rem; color: #BBBBBB;'>Motor de ETL dinâmico. Limpe, estruture e padronize planilhas complexas em milissegundos, preservando a integridade do modelo original.</p>", 
                unsafe_allow_html=True
            )
            
    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='color:#f4a261;'>📈 Análise</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='font-size: 0.9rem; color: #BBBBBB;'>Gere dashboards interativos, acompanhe KPIs vitais e aplique formatações avançadas para transformar dados crus em direcionamentos estratégicos.</p>", 
                unsafe_allow_html=True
            )
            
    with col3:
        with st.container(border=True):
            st.markdown("<h3 style='color:#9b5de5;'>🤖 Inteligência</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='font-size: 0.9rem; color: #BBBBBB;'>Integração nativa com IA. Receba relatórios explicativos, auditoria de dados e correção automática de queries SQL no console dedicado.</p>", 
                unsafe_allow_html=True
            )

    # Rodapé Discreto
    st.markdown(
        """
        <div style="text-align: center; padding-top: 3rem;">
            <p style="color: #555555; font-size: 0.8rem;">
                PocketDBA © 2026 | Desenvolvido para simplificar rotinas corporativas.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
          )
