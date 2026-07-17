# app.py
import streamlit as st
import pandas as pd

# Configuração global de layout da página (Debe ser a primeira linha do Streamlit)
st.set_page_config(
    page_title="PocketDBA",
    page_icon="📊",
    layout="wide"
)

# Importações dos seus módulos corrigidos e modernizados
from modules.interface import render_header, render_sidebar
from modules.home import render_home
from modules.planilhas import render_planilhas
from modules.console_sql import render_console_sql
from modules.dashboard import render_dashboard

def main():
    # 1. Renderiza o Cabeçalho Global (Roxo e Laranja)
    render_header()
    
    # 2. Renderiza a Sidebar Moderna (Pills e Segmented Controls)
    pagina = render_sidebar()
    
    # 3. Gerenciamento de Estado da Planilha Ativa
    # Inicializa um DataFrame vazio padrão caso o usuário acesse o Dashboard ou SQL antes de upar algo
    if "planilha_ativa_nome" not in st.session_state:
        st.session_state.planilha_ativa_nome = "Base_Corporativa"
    
    if "planilhas" not in st.session_state:
        st.session_state.planilhas = {}
        
    if st.session_state.planilha_ativa_nome not in st.session_state.planilhas:
        # Cria um DataFrame estrutural de exemplo para o app não quebrar vazio
        st.session_state.planilhas[st.session_state.planilha_ativa_nome] = pd.DataFrame(
            columns=["Descrição", "Categoria", "Data", "Valor", "Observações"]
        )

    nome_atual = st.session_state.planilha_ativa_nome
    df_atual = st.session_state.planilhas[nome_atual]

    # 4. Roteamento Inteligente de Páginas
    if pagina == "[🏠] Início":
        render_home()
        
        # Botão de atalho Corporativo "Começar Agora" direto na Home
        st.markdown("<div style='text-align: center; padding-top: 1rem;'></div>", unsafe_allow_html=True)
        col_space1, col_btn, col_space2 = st.columns([2, 1, 2])
        with col_btn:
            if st.button("🚀 Carregar minha Planilha", use_container_width=True):
                # Força a navegação para a aba de planilhas injetando no query_params ou session_state se necessário
                st.info("Clique em '[🧾] Planilhas' no menu lateral para iniciar o mapeamento.")

    elif pagina == "[🧾] Planilhas":
        render_planilhas(df_atual, nome_atual)

    elif pagina == "[💻] Console SQL":
        render_console_sql(df_atual, nome_atual)

    elif pagina == "[📈] Dashboard":
        # Captura as variáveis de configuração da sidebar (com fallbacks de segurança)
        filtros_on = st.session_state.get("modo_pocketdba") == "Completo"
        meta_orcamento = 0.0
        mostrar_kpis = True
        mostrar_graficos = True
        
        # Inspeciona dinamicamente as colunas para não quebrar o dashboard corporativo
        colunas_disponiveis = list(df_atual.columns)
        coluna_kpi = colunas_disponiveis[0] if colunas_disponiveis else None
        coluna_graf = colunas_disponiveis[1] if len(colunas_disponiveis) > 1 else coluna_kpi
        cor_grafico = st.session_state.get("cor_grafico", "#9b5de5")

        render_dashboard(
            df=df_atual,
            nome=nome_atual,
            filtros_on=filtros_on,
            meta_orcamento=meta_orcamento,
            mostrar_kpis=mostrar_kpis,
            coluna_kpi=coluna_kpi,
            coluna_graf=coluna_graf,
            destacar_outliers=False,
            mostrar_graficos=mostrar_graficos,
            grafico_donut_on=True,
            grafico_barras_on=True,
            grafico_linha_on=True,
            grafico_histograma_on=False,
            grafico_boxplot_on=False,
            df_filtrado=df_atual, # Passa a base higienizada pelo novo ETL
            cor=cor_grafico
        )

if __name__ == "__main__":
    main()
