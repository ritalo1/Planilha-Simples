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

    # Estado global das planilhas
    if "planilhas" not in st.session_state:
        st.session_state.planilhas = {}
    if nome not in st.session_state.planilhas:
        st.session_state.planilhas[nome] = df

    # Importador de Arquivos
    st.subheader("[📥] Importar planilha")
    arquivo = st.file_uploader(
        "Selecione um arquivo para mapeamento",
        type=["xlsx", "xlsm", "ods", "csv", "tsv"],
        key=f"upload_{nome}"
    )

    if arquivo:
        nome_arquivo = arquivo.name.lower()
        if nome_arquivo.endswith((".csv", ".tsv")):
            df_importado = pd.read_csv(arquivo)
        else:
            df_importado = pd.read_excel(arquivo)

        df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()].copy()
        st.session_state.planilhas[nome] = df_importado
        st.success("[📐] Planilha importada com sucesso.")

    # Puxa os dados para exibição
    df_atual = st.session_state.planilhas[nome]
    df_atual = df_atual.loc[:, ~df_atual.columns.duplicated()].copy()
    df_atual = df_atual.reset_index(drop=True)

    # Exibe o mapeamento automático de letras
    col_letters = _col_letters(len(df_atual.columns))
    header = " | ".join(f"{letra}: {col}" for letra, col in zip(col_letters, df_atual.columns))
    st.markdown(f"<p style='font-size:12px; color:#BBBBBB;'>Mapeamento de Colunas: {header}</p>", unsafe_allow_html=True)

    # Exibição dos valores normais na tela
    st.subheader("[📊] Visualização dos Dados")
    st.dataframe(df_atual, use_container_width=True)

    # --- NOVO: LOCALIZAR E SUBSTITUIR EM LOTE ---
    st.markdown("### [🔍] Localizar e Substituir")
    col_loc, col_sub, col_go = st.columns([2, 2, 1])
    
    with col_loc:
        termo_busca = st.text_input("Localizar:", placeholder="Texto ou número...", key=f"loc_{nome}")
    with col_sub:
        termo_subst = st.text_input("Substituir por:", placeholder="Novo valor...", key=f"sub_{nome}")
    with col_go:
        st.markdown("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Aplicar", key=f"btn_sub_{nome}", use_container_width=True):
            if termo_busca:
                # Substitui em todas as colunas do DataFrame
                df_atual = df_atual.replace(termo_busca, termo_subst)
                st.session_state.planilhas[nome] = df_atual
                st.success(f"Substituído '{termo_busca}' por '{termo_subst}'!")
                st.rerun()

    # --- INTERFACE DE LIMPEZA COM INSTRUÇÃO PARA A IA ---
    st.markdown("### [🧹] Limpar planilha")
    
    col_btn, col_ia = st.columns([1, 2])

    with col_btn:
        st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
        limpar = st.button("🧹 Limpar dados", key=f"btn_limpar_{nome}")
        
    with col_ia:
        usar_ia = st.checkbox(
            "Com auxílio do PocketDBA",
            value=False,
            key=f"ia_limpar_{nome}"
        )

    # Se marcar a caixinha da IA, abre dinamicamente o espaço do Prompt
    prompt_usuario = ""
    if usar_ia:
        prompt_usuario = st.text_area(
            "🧠 Instruções para o PocketDBA:",
            placeholder="Ex: Formate a coluna 'Valor' para float, remova CPFs duplicados, corrija nomes errados...",
            key=f"prompt_ia_{nome}",
            help="Diga exatamente o que você quer que a inteligência faça na limpeza dessa planilha."
        )

    if limpar:
        # Passamos as instruções que você digitou direto para a sua função de ETL
        df_limpo = limpar_planilha(
            df_atual,
            usar_ia=usar_ia,
            ia_resumo_fn=resumo_planilha if usar_ia else None,
            instrucoes_ia=prompt_usuario if usar_ia else ""  # Enviando o prompt pro seu ETL
        )
        st.session_state.planilhas[nome] = df_limpo
        st.success("Planilha processada com sucesso!")
        st.rerun()

    # Bloco de ações
    st.markdown("### [📦] Ações")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.download_button(
            label="[📤] Exportar para Excel",
            data=to_excel(df_atual),
            file_name=f"{nome}.xlsx",
            key=f"download_{nome}"
        )

    with col_b2:
        if "Valor" in df_atual.columns:
            total = pd.to_numeric(df_atual["Valor"], errors="coerce").sum()
            st.success(f"Total de valores em {nome}: {total:,.2f}")
        else:
            st.info("Nenhuma coluna 'Valor' encontrada.")
