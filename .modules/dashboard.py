import streamlit as st
import altair as alt
import pandas as pd

def render_dashboard(df, nome, filtros_on, meta_orcamento, mostrar_kpis,
                     coluna_kpi, coluna_graf, destacar_outliers,
                     mostrar_graficos, grafico_donut_on, grafico_barras_on,
                     grafico_linha_on, grafico_histograma_on, grafico_boxplot_on,
                     df_filtrado, cor):

    st.markdown(f"<h3 style='color:#4CAF50;'>📊 Dashboard — {nome}</h3>", unsafe_allow_html=True)

    if df.empty:
        st.warning("Planilha vazia.")
        return

    df_kpi = df_filtrado.copy()

    if mostrar_kpis:
        st.markdown("#### 📌 Indicadores")

        if meta_orcamento > 0:
            total = df_filtrado["Valor"].sum()
            pct = (total / meta_orcamento) * 100
            st.markdown(f"**Uso do orçamento: {pct:.1f}%**")
            st.progress(min(pct / 100, 1.0))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de lançamentos", len(df_filtrado))
        with col2:
            st.metric("Valores únicos", df_filtrado[coluna_kpi].nunique())
        with col3:
            modo = df_filtrado[coluna_kpi].mode()
            st.metric("Mais frequente", str(modo.iloc[0]) if not modo.empty else "N/A")

    if mostrar_graficos:
        st.markdown("#### 📊 Gráficos")

        df_cat = df_filtrado.groupby("Categoria", as_index=False)["Valor"].sum()

        if grafico_donut_on:
            chart = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
                theta="Valor:Q",
                color="Categoria:N",
                tooltip=["Categoria", "Valor"]
            )
            st.altair_chart(chart, use_container_width=True)

        if grafico_barras_on:
            chart = alt.Chart(df_cat).mark_bar(color=cor).encode(
                x="Categoria:N",
                y="Valor:Q"
            )
            st.altair_chart(chart, use_container_width=True)

        if grafico_linha_on:
            df_linha = df_filtrado.dropna(subset=["Data"])
            if not df_linha.empty:
                chart = alt.Chart(df_linha).mark_line(color=cor).encode(
                    x="Data:T",
                    y="Valor:Q"
                )
                st.altair_chart(chart, use_container_width=True)
