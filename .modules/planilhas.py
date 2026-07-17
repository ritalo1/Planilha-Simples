import streamlit as st
import pandas as pd
from modules.etl import limpar_planilha
from modules.utils import to_excel

def render_planilhas(df, nome):
    st.markdown(f"<h3 style='color:#4CAF50;'>🧾 Planilha — {nome}</h3>", unsafe_allow_html=True)

    st.subheader("📥 Importar planilha")
    arquivo = st.file_uploader("Selecione um arquivo", type=["xlsx", "csv", "tsv"], key=f"upload_{nome}")

    if arquivo:
        nome_arquivo = arquivo.name.lower()
        if nome_arquivo.endswith((".csv", ".tsv")):
            df_importado = pd.read_csv(arquivo)
        else:
            df_importado = pd.read_excel(arquivo)

        colunas = list(df_importado.columns)

        col_desc = st.selectbox("Descrição", colunas)
        col_cat = st.selectbox("Categoria", colunas)
        col_val = st.selectbox("Valor", colunas)
        col_data = st.selectbox("Data", colunas)

        if st.button("Confirmar"):
            df_importado = df_importado.rename(columns={
                col_desc: "Descrição",
                col_cat: "Categoria",
                col_val: "Valor",
                col_data: "Data"
            })
            df_importado = limpar_planilha(df_importado)
            st.session_state.planilhas[nome] = df_importado
            df = df_importado
            st.success("Planilha importada e limpa.")

    st.subheader("✏️ Editar dados")
    st.session_state.planilhas[nome] = st.data_editor(
        df,
        num_rows="dynamic",
        key=f"editor_{nome}",
        use_container_width=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧹 Limpar"):
            df_limpo = limpar_planilha(st.session_state.planilhas[nome])
            st.session_state.planilhas[nome] = df_limpo
            st.success("Limpa!")

    with col2:
        if st.button("🧮 Total"):
            total = df["Valor"].sum()
            st.success(f"Total: R$ {total:,.2f}")

    with col3:
        st.download_button(
            "📤 Exportar Excel",
            data=to_excel(df),
            file_name=f"{nome}.xlsx"
        )
