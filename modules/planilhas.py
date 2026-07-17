import streamlit as st
import pandas as pd
from modules.etl import limpar_planilha
from modules.utils import to_excel

def render_planilhas(df, nome):
    st.markdown(f"<h3 style='color:#4CAF50;'>🧾 Planilha — {nome}</h3>", unsafe_allow_html=True)

    st.subheader("📥 Importar planilha")
    arquivo = st.file_uploader(
        "Selecione um arquivo",
        type=["xlsx", "xlsm", "ods", "csv", "tsv"],
        key=f"upload_{nome}"
    )

    if arquivo:
        nome_arquivo = arquivo.name.lower()

        # Importação segura
        if nome_arquivo.endswith((".csv", ".tsv")):
            df_importado = pd.read_csv(arquivo)
        else:
            df_importado = pd.read_excel(arquivo)

        # Remove colunas duplicadas
        df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()]

        colunas_detectadas = list(df_importado.columns)

        st.info("Mapeie as colunas do arquivo para o padrão do sistema:")

        col_desc = st.selectbox("Coluna de Descrição", colunas_detectadas, key=f"map_desc_{nome}")
        col_cat = st.selectbox("Coluna de Categoria", colunas_detectadas, key=f"map_cat_{nome}")
        col_val = st.selectbox("Coluna de Valor", colunas_detectadas, key=f"map_val_{nome}")
        col_data = st.selectbox("Coluna de Data", colunas_detectadas, key=f"map_data_{nome}")

        if st.button("Confirmar mapeamento e limpar", key=f"map_btn_{nome}"):

            # Renomeação segura
            df_importado = df_importado.rename(columns={
                col_desc: "Descrição",
                col_cat: "Categoria",
                col_val: "Valor",
                col_data: "Data"
            })

            # Remove duplicatas novamente após renomear
            df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()]

            # ETL
            df_importado = limpar_planilha(df_importado)

            st.session_state.planilhas[nome] = df_importado
            df = df_importado

            st.success("Planilha importada, mapeada e limpa com sucesso!")

    # ============================
# EDITOR DE DADOS
# ============================

st.subheader("✏️ Editar dados")
df = st.session_state.planilhas[nome]

# Remover duplicatas ANTES do editor
df = df.loc[:, ~df.columns.duplicated()].copy()

# Resetar índice (evita colunas internas do Streamlit)
df = df.reset_index(drop=True)

# Editor seguro
st.session_state.planilhas[nome] = st.data_editor(
    df,
    num_rows="dynamic",
    key=f"editor_{nome}",
    use_container_width=True
)

    # ============================
    # BOTÕES
    # ============================

    col_b1, col_b2, col_b3 = st.columns(3)

    with col_b1:
        if st.button(f"🧹 Limpar planilha — {nome}"):
            df_limpo = limpar_planilha(st.session_state.planilhas[nome])
            st.session_state.planilhas[nome] = df_limpo
            st.success("Planilha limpa.")

    with col_b2:
        if st.button(f"🧮 Calcular total — {nome}"):
            df_calc = limpar_planilha(st.session_state.planilhas[nome].copy())
            total = df_calc["Valor"].sum()
            st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")

    with col_b3:
        df_export = st.session_state.planilhas[nome]
        st.download_button(
            label="📤 Exportar para Excel",
            data=to_excel(df_export),
            file_name=f"{nome}.xlsx"
                )
