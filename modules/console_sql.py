import streamlit as st
import duckdb
from modules.ia_sql import corrigir_sql
from modules.utils import to_excel

def render_console_sql(df, nome):
    st.markdown(f"<h3 style='color:#4CAF50;'>💻 Console SQL — {nome}</h3>", unsafe_allow_html=True)

    sql_query = st.text_area("SQL:", height=150)

    if st.button("⚡ Executar"):
        sql_corrigido = corrigir_sql(sql_query)

        try:
            resultado = duckdb.query(sql_corrigido).to_df()
            st.dataframe(resultado, use_container_width=True)

            st.download_button(
                "📥 Baixar Excel",
                data=to_excel(resultado),
                file_name="resultado.xlsx"
            )

        except Exception as e:
            st.error(f"Erro: {e}")
