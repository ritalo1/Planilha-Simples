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
        "<p style='color:#BBBBBB; font-size:14px;'>Edite, desenhe e limpe suas planilhas com auxílio opcional do PocketDBA.</p>",
        unsafe_allow_html=True
    )

    # Nome da planilha editável
    novo_nome = st.text_input("Nome da planilha:", value=nome, key=f"nome_planilha_{nome}")

    # Importar
    st.subheader("[📥] Importar planilha")
    arquivo = st.file_uploader(
        "Selecione um arquivo",
        type=["xlsx", "xlsm", "ods", "csv", "tsv"],
        key=f"upload_{nome}"
    )

    if "planilhas" not in st.session_state:
        st.session_state.planilhas = {}
    if novo_nome not in st.session_state.planilhas:
        st.session_state.planilhas[novo_nome] = df

    if arquivo:
        nome_arquivo = arquivo.name.lower()

        if nome_arquivo.endswith((".csv", ".tsv")):
            df_importado = pd.read_csv(arquivo)
        else:
            df_importado = pd.read_excel(arquivo)

        df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()].copy()
        st.session_state.planilhas[novo_nome] = df_importado
        st.success("[📐] Planilha desenhada com sucesso (sem limpeza automática).")

    # Editor
    st.subheader("[✏️] Desenhar planilha (editor)")
    df = st.session_state.planilhas[novo_nome]
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df = df.reset_index(drop=True)

    # Cabeçalho com letras de coluna
    col_letters = _col_letters(len(df.columns))
    header = " | ".join(f"{letra}: {col}" for letra, col in zip(col_letters, df.columns))
    st.markdown(f"<p style='font-size:12px; color:#BBBBBB;'>Colunas: {header}</p>", unsafe_allow_html=True)

    # Editor de dados + nomes de colunas editáveis
    col_names = st.text_input(
        "Renomear colunas (separadas por vírgula, na ordem atual):",
        value=", ".join(df.columns),
        key=f"col_names_{novo_nome}"
    )
    novos_nomes = [c.strip() for c in col_names.split(",")] if col_names.strip() else df.columns
    if len(novos_nomes) == len(df.columns):
        df.columns = novos_nomes

    st.session_state.planilhas[novo_nome] = st.data_editor(
        df,
        num_rows="dynamic",
        key=f"editor_{novo_nome}",
        use_container_width=True
    )

    # Limpeza condicionada ao botão + switch IA
    st.markdown("### [🧹] Limpar planilha")
    col_l1, col_l2 = st.columns([2, 2])

    with col_l1:
        limpar = st.button("🧹 Limpar dados", key=f"btn_limpar_{novo_nome}")
    with col_l2:
        usar_ia = st.checkbox(
            "Com auxílio do PocketDBA",
            value=False,
            key=f"ia_limpar_{novo_nome}"
        )

    if limpar:
        df_atual = st.session_state.planilhas[novo_nome]
        df_limpo = limpar_planilha(
            df_atual,
            usar_ia=usar_ia,
            ia_resumo_fn=resumo_planilha if usar_ia else None
        )
        st.session_state.planilhas[novo_nome] = df_limpo
        st.success("Planilha limpa. Editor atualizado abaixo.")
        st.dataframe(df_limpo, use_container_width=True)

    # Ações
    st.markdown("### [📦] Ações")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        df_export = st.session_state.planilhas[novo_nome]
        st.download_button(
            label="[📤] Exportar para Excel",
            data=to_excel(df_export),
            file_name=f"{novo_nome}.xlsx"
        )

    with col_b2:
        df_calc = st.session_state.planilhas[novo_nome]
        if "Valor" in df_calc.columns:
            total = pd.to_numeric(df_calc["Valor"], errors="coerce").sum()
            st.success(f"Total de valores em {novo_nome}: {total:,.2f}")
        else:
            st.info("Nenhuma coluna 'Valor' encontrada para cálculo.")
