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
        "<p style='color:#BBBBBB; font-size:14px;'>Visualize e gerencie a estrutura da sua planilha mapeada automaticamente.</p>",
        unsafe_allow_html=True
    )

    # Estado global das planilhas
    if "planilhas" not in st.session_state:
        st.session_state.planilhas = {}
    if nome not in st.session_state.planilhas:
        st.session_state.planilhas[nome] = df

    # Importador de Arquivos Direto
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
        st.success("[📐] Planilha importada e mapeada com sucesso.")

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

    # --- BLOCO DE LIMPEZA LADO A LADO ---
    st.markdown("### [🧹] Limpar planilha")
    
    # Criamos colunas bem ajustadas para o mobile: 
    # A primeira coluna pega o botão, a segunda fica colada com o Checkbox da IA
    col_btn, col_ia = st.columns([1, 2])

    with col_btn:
        limpar = st.button("🧹 Limpar dados", key=f"btn_limpar_{nome}")
        
    with col_ia:
        # Esse markdown serve apenas para empurrar o checkbox um pouquinho para baixo,
        # fazendo ele ficar perfeitamente alinhado no meio do botão ao lado.
        st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
        usar_ia = st.checkbox(
            "Com auxílio do PocketDBA",
            value=False,
            key=f"ia_limpar_{nome}"
        )

    if limpar:
        df_limpo = limpar_planilha(
            df_atual,
            usar_ia=usar_ia,
            ia_resumo_fn=resumo_planilha if usar_ia else None
        )
        st.session_state.planilhas[nome] = df_limpo
        st.success("Planilha limpa com sucesso!")
        st.rerun()

    # Bloco simples de ações
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
            st.info("Nenhuma coluna 'Valor' encontrada para cálculo rápido.")
