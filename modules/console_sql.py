import streamlit as st
import duckdb
from modules.ia_sql import corrigir_sql
from modules.utils import to_excel

def render_console_sql(df, nome):
    st.markdown(
        f"<h3 style='color:#9b5de5;'>[💻] Console SQL — {nome}</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#BBBBBB; font-size:14px;'>Execute consultas SQL com correção automática de sintaxe.</p>",
        unsafe_allow_html=True
    )

    sql_query = st.text_area("Digite sua consulta SQL:", height=150)

    if st.button("⚡ Executar"):
        try:
            sql_corrigido = corrigir_sql(sql_query)
            resultado = duckdb.query(sql_corrigido).to_df()
            st.dataframe(resultado, use_container_width=True)

            st.download_button(
                "[📥] Baixar resultado em Excel",
                data=to_excel(resultado),
                file_name="resultado_sql.xlsx"
            )

        except Exception as e:
            st.error(f"Erro ao executar SQL: {e}")
