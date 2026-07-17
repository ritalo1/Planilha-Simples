import streamlit as st
import altair as alt
import pandas as pd

def render_dashboard(df, nome, filtros_on, meta_orcamento, mostrar_kpis,
                     coluna_kpi, coluna_graf, destacar_outliers,
                     mostrar_graficos, grafico_donut_on, grafico_barras_on,
                     grafico_linha_on, grafico_histograma_on, grafico_boxplot_on,
                     df_filtrado, cor):

    st.markdown(f"<h3 style='color:#f4a261;'>📊 Dashboard — {nome}</h3>", unsafe_allow_html=True)

    if df.empty:
        st.warning("Planilha vazia.")
        return

    df_kpi = df_filtrado.copy()

    if mostrar_kpis:
        st.markdown("#### 📌 Indicadores Principais")

        if meta_orcamento > 0:
            with st.container(border=True):
                total = df_filtrado["Valor"].sum()
                pct = (total / meta_orcamento) * 100
                st.markdown(f"**Uso do orçamento: {pct:.1f}%**")
                st.progress(min(pct / 100, 1.0))

        col1, col2, col3 = st.columns(3)
        # Envelopando os KPIs em containers com borda
        with col1:
            with st.container(border=True):
                st.metric("Total Lançamentos", len(df_filtrado), help="Contagem de registros válidos na planilha.")
        with col2:
            with st.container(border=True):
                st.metric("Valores Únicos", df_filtrado[coluna_kpi].nunique())
        with col3:
            with st.container(border=True):
                modo = df_filtrado[coluna_kpi].mode()
                st.metric("Mais Frequente", str(modo.iloc[0]) if not modo.empty else "N/A")

    if mostrar_graficos:
        st.markdown("#### 📈 Visões Gráficas")

        df_cat = df_filtrado.groupby("Categoria", as_index=False)["Valor"].sum()

        if grafico_donut_on:
            with st.container(border=True):
                chart = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
                    theta="Valor:Q",
                    color=alt.Color("Categoria:N", scale=alt.Scale(scheme='purples')),
                    tooltip=["Categoria", "Valor"]
                ).properties(title="Distribuição por Categoria")
                st.altair_chart(chart, use_container_width=True)

        if grafico_barras_on:
            with st.container(border=True):
                chart = alt.Chart(df_cat).mark_bar(color=cor).encode(
                    x="Categoria:N",
                    y="Valor:Q"
                )
                st.altair_chart(chart, use_container_width=True)

        if grafico_linha_on:
            df_linha = df_filtrado.dropna(subset=["Data"])
            if not df_linha.empty:
                with st.container(border=True):
                    chart = alt.Chart(df_linha).mark_line(color=cor, point=True).encode(
                        x="Data:T",
                        y="Valor:Q",
                        tooltip=["Data:T", "Valor:Q"]
                    )
                    st.altair_chart(chart, use_container_width=True)
