import streamlit as st
import pandas as pd
from string import ascii_uppercase

from modules.etl import limpar_planilha
from modules.utils import to_excel
from modules.ia_sql import resumo_planilha

def _col_letters(n_cols):
    letras = []
    for i in range(n_cols):
        div, mod = divmod(i, 26)
        letra = ascii_uppercase[mod]
        if div > 0:
            letra = ascii_uppercase[div - 1] + letra
        letras.append(letra)
    return letras

def render_planilhas(df, nome):
    st.markdown(
        f"<h3 style='color:#9b5de5;'>[🧾] Planilhas — {nome}</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#BBBBBB; font-size:14px;'>Visualize, trate e limpe sua planilha mapeada automaticamente.</p>",
        unsafe_allow_html=True
    )

    # Estado global das planilhas e dos logs de auditoria no session_state
    if "planilhas" not in st.session_state:
        st.session_state.planilhas = {}
    if nome not in st.session_state.planilhas:
        st.session_state.planilhas[nome] = df
        
    # Inicializa o cache do relatório da IA para não perder no clique dos botões
    if "ultimo_resumo_ia" not in st.session_state:
        st.session_state.ultimo_resumo_ia = {}
    if nome not in st.session_state.ultimo_resumo_ia:
        st.session_state.ultimo_resumo_ia[nome] = None

    # ==========================================
    # 1. IMPORTAÇÃO DE ARQUIVOS
    # ==========================================
    st.subheader("[📥] Importar planilha")
    arquivo = st.file_uploader(
        "Selecione um arquivo para mapeamento",
        type=["xlsx", "xlsm", "ods", "csv", "tsv"],
        key=f"upload_arquivo_input_{nome}"
    )

    if arquivo:
        nome_arquivo = arquivo.name.lower()
        if nome_arquivo.endswith((".csv", ".tsv")):
            df_importado = pd.read_csv(arquivo)
        else:
            df_importado = pd.read_excel(arquivo)

        df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()].copy()
        st.session_state.planilhas[nome] = df_importado
        st.session_state.ultimo_resumo_ia[nome] = None # Reseta o resumo para a nova planilha
        st.success("[📐] Planilha importada com sucesso.")

    # Puxa os dados atuais para renderização
    df_atual = st.session_state.planilhas[nome]
    df_atual = df_atual.loc[:, ~df_atual.columns.duplicated()].copy()
    df_atual = df_atual.reset_index(drop=True)

    # Exibe o mapeamento automático de letras estilo Excel
    col_letters = _col_letters(len(df_atual.columns))
    header = " | ".join(f"{letra}: {col}" for letra, col in zip(col_letters, df_atual.columns))
    st.markdown(f"<p style='font-size:12px; color:#BBBBBB;'>Mapeamento de Colunas: {header}</p>", unsafe_allow_html=True)

    # ==========================================
    # 2. VISUALIZAÇÃO DOS DADOS
    # ==========================================
    st.subheader("[📊] Visualização dos Dados")
    st.dataframe(df_atual, use_container_width=True)

    # ==========================================
    # 3. LOCALIZAR E SUBSTITUIR (MANUAL EM LOTE)
    # ==========================================
    st.markdown("### [🔍] Localizar e Substituir")
    col_loc, col_sub, col_go = st.columns([2, 2, 1])
    
    with col_loc:
        termo_busca = st.text_input("Localizar:", placeholder="Texto ou número...", key=f"txt_localizar_alvo_{nome}")
    with col_sub:
        termo_subst = st.text_input("Substituir por:", placeholder="Novo valor...", key=f"txt_substituir_novo_{nome}")
    with col_go:
        st.markdown("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Aplicar", key=f"btn_manual_sub_trigger_{nome}", use_container_width=True):
            if termo_busca:
                df_atual = df_atual.replace(termo_busca, termo_subst)
                st.session_state.planilhas[nome] = df_atual
                st.success(f"Substituído '{termo_busca}' por '{termo_subst}'!")
                st.rerun()

    # ==========================================
    # 4. PIPELINE DE LIMPEZA (ETL + IA)
    # ==========================================
    st.markdown("### [🧹] Limpar planilha")
    
    col_btn, col_ia = st.columns([1, 2])

    with col_btn:
        st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
        limpar_simples = st.button("🧹 Limpar dados simples", key=f"btn_limpar_simples_click_{nome}")
        
    with col_ia:
        usar_ia = st.checkbox(
            "Com auxílio do PocketDBA",
            value=False,
            key=f"chk_usar_ia_ativador_{nome}"
        )

    # Se a IA estiver ativa, abre o form compacto de envio rápido com a setinha
    prompt_usuario = ""
    limpar_com_ia = False
    
    if usar_ia:
        with st.form(key=f"form_ia_limpeza_escopo_{nome}", border=True):
            prompt_usuario = st.text_area(
                "🧠 Instruções para o PocketDBA:",
                placeholder="Ex: Formate a coluna 'Valor' para float, remova CPFs duplicados...",
                key=f"txt_prompt_ia_comando_{nome}",
                help="Diga exatamente o que você quer que a inteligência faça na limpeza."
            )
            
            col_space, col_submit = st.columns([4, 1])
            with col_submit:
                limpar_com_ia = st.form_submit_button("➡️ Enviar", use_container_width=True)

    # Disparo do processo de ETL
    if limpar_simples or limpar_com_ia:
        with st.spinner("PocketDBA processando o pipeline de ETL..."):
            # 1. Executa a limpeza estrutural de dados primeiro
            df_limpo = limpar_planilha(
                df_atual,
                usar_ia=False,
                ia_resumo_fn=None
            )
            
            # 2. Se o usuário usou a IA, dispara de forma isolada e segura
            if limpar_com_ia and usar_ia:
                relatorio_ia = resumo_planilha(df_limpo, instrucoes_ia=prompt_usuario)
                st.session_state.ultimo_resumo_ia[nome] = {
                    "prompt": prompt_usuario if prompt_usuario else "Limpeza padrão de IA.",
                    "resultado": relatorio_ia
                }
        
        st.session_state.planilhas[nome] = df_limpo
        st.success("Planilha processada com sucesso!")
        st.rerun()

    # Renderiza o expander caso exista um relatório salvo no estado da sessão
    if st.session_state.ultimo_resumo_ia[nome] is not None:
        with st.expander("📋 Ver detalhes técnicos e logs do PocketDBA", expanded=True):
            st.markdown("**Instruções aplicadas no pipeline:**")
            st.code(st.session_state.ultimo_resumo_ia[nome]["prompt"])
            
            st.markdown("---")
            # Identidade visual montada de forma segura na interface
            st.markdown("### <span style='color:#9b5de5;'>[📊] Pocket</span><span style='color:#f4a261;'>DBA</span>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Renderiza o texto puro em Markdown perfeitamente
            st.markdown(st.session_state.ultimo_resumo_ia[nome]["resultado"])

    # ==========================================
    # 5. BLOCO DE AÇÕES FINAIS
    # ==========================================
    st.markdown("### [📦] Ações")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.download_button(
            label="[📤] Exportar para Excel",
            data=to_excel(st.session_state.planilhas[nome]),
            file_name=f"{nome}.xlsx",
            key=f"btn_download_final_excel_{nome}"
        )

    with col_b2:
        df_calc = st.session_state.planilhas[nome]
        if "Valor" in df_calc.columns:
            total = pd.to_numeric(df_calc["Valor"], errors="coerce").sum()
            st.success(f"Total de valores em {nome}: {total:,.2f}")
        else:
            st.info("Nenhuma coluna 'Valor' encontrada.")
