import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

# ============================
# FUNÇÕES UTILITÁRIAS
# ============================

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, index=False, sheet_name="Gastos")
    writer.close()
    return output.getvalue()

def limpar_planilha(df):
    # Remove colunas Unnamed
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Remove linhas totalmente vazias
    df = df.dropna(how="all")

    # Padroniza colunas
    df.columns = df.columns.str.strip().str.title()

    # Garante colunas esperadas
    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Converte tipos básicos
    df["Descrição"] = df["Descrição"].astype(str).str.strip()
    df["Categoria"] = df["Categoria"].astype(str).str.strip()
    df["Observações"] = df["Observações"].astype(str).str.strip()

    # Converte datas
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Converte valores (tratando R$, ponto e vírgula)
    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)

    return df

def aplicar_filtros(df, filtros_on, categorias_sel, data_ini, data_fim, vmin, vmax, texto):
    if not filtros_on:
        return df

    df_filtrado = df.copy()

    # Categoria
    if categorias_sel:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias_sel)]

    # Datas
    df_filtrado = df_filtrado[
        (df_filtrado["Data"] >= pd.to_datetime(data_ini)) &
        (df_filtrado["Data"] <= pd.to_datetime(data_fim))
    ]

    # Valores
    df_filtrado = df_filtrado[
        (df_filtrado["Valor"] >= vmin) &
        (df_filtrado["Valor"] <= vmax)
    ]

    # Texto na descrição
    if texto.strip():
        df_filtrado = df_filtrado[
            df_filtrado["Descrição"].str.contains(texto, case=False, na=False)
        ]

    return df_filtrado

# ============================
# FUNÇÕES DE KPIs
# ============================

def kpi_valores_unicos(df, coluna):
    total = df[coluna].nunique()
    st.metric(f"Valores únicos em {coluna}", total)

def kpi_frequencia(df, coluna):
    freq = df[coluna].value_counts().reset_index()
    freq.columns = [coluna, "Frequência"]
    st.subheader(f"📊 Frequência de {coluna}")
    st.dataframe(freq)

def kpi_mais_comum(df, coluna):
    comum = df[coluna].mode()
    if not comum.empty:
        st.info(f"🔎 Valor mais comum em {coluna}: {comum.iloc[0]}")

def kpi_total_categoria(df_kpi):
    df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
    df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
    st.subheader("📊 Total por categoria")
    st.dataframe(df_cat)
    return df_cat

def kpi_ticket_medio(df_kpi):
    df_ticket = df_kpi.groupby("Categoria", as_index=False)["Valor"].mean()
    df_ticket.rename(columns={"Valor": "Ticket Médio"}, inplace=True)
    st.subheader("💳 Ticket médio por categoria")
    st.dataframe(df_ticket)

def kpi_dia_max(df_kpi):
    df_data = df_kpi.dropna(subset=["Data"])
    if not df_data.empty:
        dia_max = df_data.loc[df_data["Valor"].idxmax()]
        st.info(f"📅 Dia com maior gasto: {dia_max['Data'].date()} — R$ {dia_max['Valor']:,.2f}")

# ============================
# FUNÇÕES DE GRÁFICOS
# ============================

def grafico_barras_generico(df, coluna, cor):
    freq = df[coluna].value_counts().reset_index()
    freq.columns = [coluna, "Frequência"]

    grafico = alt.Chart(freq).mark_bar(color=cor).encode(
        x=alt.X(coluna, type="nominal"),
        y=alt.Y("Frequência:Q")
    )

    st.subheader(f"📊 Frequência de {coluna}")
    st.altair_chart(grafico, use_container_width=True)

def grafico_pizza(df_cat):
    grafico = alt.Chart(df_cat).mark_arc().encode(
        theta="Valor",
        color="Categoria",
        tooltip=["Categoria", "Valor", "Percentual"]
    )
    st.subheader("🍕 Distribuição por categoria")
    st.altair_chart(grafico, use_container_width=True)

def grafico_barras(df, cor):
    grafico = alt.Chart(df).mark_bar(
        cornerRadiusTopLeft=5,
        cornerRadiusTopRight=5,
        color=cor
    ).encode(
        x=alt.X("Categoria", sort="-y"),
        y="Valor"
    )
    st.subheader("📊 Gastos por categoria")
    st.altair_chart(grafico, use_container_width=True)

def grafico_linha(df, cor):
    df_data = df.dropna(subset=["Data"])
    grafico = alt.Chart(df_data).mark_line(
        color=cor,
        strokeWidth=3
    ).encode(
        x="Data",
        y="Valor"
    )
    st.subheader("📈 Gastos ao longo do tempo")
    st.altair_chart(grafico, use_container_width=True)

def grafico_histograma(df, cor):
    grafico = alt.Chart(df).mark_bar(color=cor).encode(
        x=alt.X("Valor", bin=alt.Bin(maxbins=20)),
        y="count()"
    )
    st.subheader("📊 Histograma de valores")
    st.altair_chart(grafico, use_container_width=True)

def grafico_boxplot(df):
    grafico = alt.Chart(df).mark_boxplot().encode(
        x="Categoria",
        y="Valor"
    )
    st.subheader("📦 Boxplot de valores por categoria")
    st.altair_chart(grafico, use_container_width=True)

# ============================
# CONFIGURAÇÕES
# ============================

CATEGORIAS = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Saúde",
    "Lazer",
    "Educação",
    "Outros"
]

MODELO = {
    "Descrição": [],
    "Categoria": [],
    "Data": [],
    "Valor": [],
    "Observações": []
}

if "planilhas" not in st.session_state:
    st.session_state.planilhas = {
        "Janeiro": pd.DataFrame(MODELO)
    }

if "cor_grafico" not in st.session_state:
    st.session_state.cor_grafico = "#4CAF50"

# ============================
# CABEÇALHO
# ============================

st.markdown(
    """
    <h1 style='text-align: center; color: #4CAF50;'>
        💸 Sistema de Gastos Mensais
    </h1>
    <p style='text-align: center; color: #CCCCCC;'>
        Ferramenta de trabalho — visão de Data Analyst Jr.
    </p>
    """,
    unsafe_allow_html=True
)

# ============================
# SIDEBAR INTELIGENTE
# ============================

with st.sidebar:
    st.markdown("## ⚙️ Menu")

    pagina = st.radio(
        "Escolha a página",
        ["Dashboard", "Planilhas"]
    )

    st.markdown("---")

    if pagina == "Dashboard":
        # Switch KPIs
        mostrar_kpis = st.checkbox("[📊] Mostrar KPIs", value=True)
        if mostrar_kpis:
            st.markdown("**[📦] Tipos de KPIs**")
            kpi_genericos = st.checkbox("KPIs genéricos", value=True)
            kpi_total_categoria_on = st.checkbox("Total por categoria", value=True)
            kpi_ticket_medio_on = st.checkbox("Ticket médio por categoria", value=True)
            kpi_dia_max_on = st.checkbox("Dia com maior gasto", value=True)

        st.markdown("---")

        # Switch Gráficos
        mostrar_graficos = st.checkbox("[📈] Mostrar gráficos", value=True)
        if mostrar_graficos:
            st.markdown("**[🧩] Tipos de gráficos**")
            grafico_generico_on = st.checkbox("Gráfico genérico (frequência)", value=True)
            grafico_pizza_on = st.checkbox("Gráfico de pizza", value=True)
            grafico_barras_on = st.checkbox("Gráfico de barras", value=True)
            grafico_linha_on = st.checkbox("Gráfico de linha", value=True)
            grafico_histograma_on = st.checkbox("Histograma de valores", value=False)
            grafico_boxplot_on = st.checkbox("Boxplot por categoria", value=False)

        st.markdown("---")

        # Filtros avançados
        filtros_on = st.checkbox("[🔎] Filtros avançados", value=False)
        if filtros_on:
            st.markdown("**Filtros**")
            # Esses controles serão usados na página Dashboard
            st.session_state.filtros_categorias = st.multiselect(
                "Categorias",
                options=list(st.session_state.planilhas.values())[0]["Categoria"].unique()
                if len(st.session_state.planilhas) > 0 else []
            )

            # Valores padrão serão ajustados na página com base no df
            st.session_state.filtros_texto = st.text_input("Buscar na descrição", "")

        st.markdown("---")

        # Configurações avançadas
        avancado_on = st.checkbox("[⚙️] Configurações avançadas de visualização", value=False)
        if avancado_on:
            st.session_state.cor_grafico = st.color_picker(
                "Cor principal dos gráficos",
                value=st.session_state.cor_grafico
            )

    elif pagina == "Planilhas":
        st.markdown("**[📥] Importação e operações**")
        st.markdown("Use a aba de cada mês para editar, limpar e exportar.")
        st.markdown("---")
        st.markdown("**[🧹] Limpeza e cálculo** na aba Planilhas.")
        st.markdown("**[📤] Exportar** também está na aba Planilhas.")

# ============================
# CONTEÚDO PRINCIPAL
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:
        df = st.session_state.planilhas[nome]

        # Limpeza básica sempre
        df = limpar_planilha(df)
        st.session_state.planilhas[nome] = df

        if pagina == "Dashboard":
            st.markdown(f"<h2 style='color:#4CAF50;'>📊 Dashboard — {nome}</h2>", unsafe_allow_html=True)

            # Seleção de colunas para KPIs e gráficos
            if len(df.columns) > 0:
                coluna_kpi = st.selectbox("Coluna para KPIs", df.columns, key=f"kpi_col_{nome}")
                coluna_grafico = st.selectbox("Coluna para gráfico genérico", df.columns, key=f"graf_col_{nome}")
            else:
                st.warning("Planilha vazia. Vá na aba Planilhas e preencha os dados.")
                continue

            # Filtros avançados (com base no df)
            if 'filtros_categorias' not in st.session_state:
                st.session_state.filtros_categorias = []

            if 'filtros_texto' not in st.session_state:
                st.session_state.filtros_texto = ""

            data_min = df["Data"].min() if not df["Data"].isna().all() else pd.to_datetime("2024-01-01")
            data_max = df["Data"].max() if not df["Data"].isna().all() else pd.to_datetime("2024-12-31")
            valor_min_default = float(df["Valor"].min()) if not df["Valor"].isna().all() else 0.0
            valor_max_default = float(df["Valor"].max()) if not df["Valor"].isna().all() else 1000.0

            if 'filtros_on' in locals() and filtros_on:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    data_ini = st.date_input("Data inicial", data_min)
                    vmin = st.number_input("Valor mínimo", value=valor_min_default)
                with col_f2:
                    data_fim = st.date_input("Data final", data_max)
                    vmax = st.number_input("Valor máximo", value=valor_max_default)

                df_filtrado = aplicar_filtros(
                    df,
                    True,
                    st.session_state.filtros_categorias,
                    data_ini,
                    data_fim,
                    vmin,
                    vmax,
                    st.session_state.filtros_texto
                )
            else:
                df_filtrado = df.copy()

            df_kpi = df_filtrado.copy()

            # KPIs
            if 'mostrar_kpis' in locals() and mostrar_kpis:
                if 'kpi_genericos' in locals() and kpi_genericos and coluna_kpi in df_filtrado.columns:
                    kpi_valores_unicos(df_filtrado, coluna_kpi)
                    kpi_frequencia(df_filtrado, coluna_kpi)
                    kpi_mais_comum(df_filtrado, coluna_kpi)

                if 'kpi_total_categoria_on' in locals() and kpi_total_categoria_on:
                    df_cat = kpi_total_categoria(df_kpi)

                if 'kpi_ticket_medio_on' in locals() and kpi_ticket_medio_on:
                    kpi_ticket_medio(df_kpi)

                if 'kpi_dia_max_on' in locals() and kpi_dia_max_on:
                    kpi_dia_max(df_kpi)

            # Gráficos
            cor = st.session_state.cor_grafico

            if 'mostrar_graficos' in locals() and mostrar_graficos:
                if 'grafico_generico_on' in locals() and grafico_generico_on and coluna_grafico in df_filtrado.columns:
                    grafico_barras_generico(df_filtrado, coluna_grafico, cor)

                if 'grafico_pizza_on' in locals() and grafico_pizza_on:
                    df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                    df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                    grafico_pizza(df_cat)

                if 'grafico_barras_on' in locals() and grafico_barras_on:
                    grafico_barras(df_kpi, cor)

                if 'grafico_linha_on' in locals() and grafico_linha_on:
                    grafico_linha(df_kpi, cor)

                if 'grafico_histograma_on' in locals() and grafico_histograma_on:
                    grafico_histograma(df_kpi, cor)

                if 'grafico_boxplot_on' in locals() and grafico_boxplot_on:
                    grafico_boxplot(df_kpi)

        elif pagina == "Planilhas":
            st.markdown(f"<h2 style='color:#4CAF50;'>🧾 Planilha — {nome}</h2>", unsafe_allow_html=True)

            st.subheader("[📥] Importar planilha")
            arquivo = st.file_uploader(
                "Selecione um arquivo",
                type=["xlsx", "xlsm", "ods", "csv", "tsv"],
                key=f"upload_{nome}"
            )

            if arquivo:
                nome_arquivo = arquivo.name.lower()

                if nome_arquivo.endswith(".csv") or nome_arquivo.endswith(".tsv"):
                    df_importado = pd.read_csv(arquivo)
                elif nome_arquivo.endswith(".xlsx") or nome_arquivo.endswith(".xlsm") or nome_arquivo.endswith(".ods"):
                    df_importado = pd.read_excel(arquivo, engine="openpyxl")
                else:
                    st.error("❌ Formato de arquivo não reconhecido.")
                    st.stop()

                df_importado = limpar_planilha(df_importado)
                st.session_state.planilhas[nome] = df_importado
                df = df_importado
                st.success("Planilha importada e limpa com sucesso!")

            st.subheader("[✏️] Editar dados")
            df = st.session_state.planilhas[nome]

            st.session_state.planilhas[nome] = st.data_editor(
                df,
                num_rows="dynamic",
                key=f"editor_{nome}",
                use_container_width=True,
                column_config={
                    "Descrição": st.column_config.TextColumn("Descrição"),
                    "Categoria": st.column_config.SelectboxColumn("Categoria", options=CATEGORIAS),
                    "Data": st.column_config.DateColumn("Data"),
                    "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "Observações": st.column_config.TextColumn("Observações")
                }
            )

            col_b1, col_b2, col_b3 = st.columns(3)

            with col_b1:
                if st.button(f"[🧹] Limpar planilha — {nome}"):
                    df_limpo = limpar_planilha(st.session_state.planilhas[nome])
                    st.session_state.planilhas[nome] = df_limpo
                    st.success("Planilha limpa com sucesso!")
                    st.dataframe(df_limpo)

            with col_b2:
                if st.button(f"[🧮] Calcular total — {nome}"):
                    df_calc = limpar_planilha(st.session_state.planilhas[nome].copy())
                    total = df_calc["Valor"].sum()
                    st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")
                    st.dataframe(df_calc)

            with col_b3:
                st.subheader("")
                df_export = st.session_state.planilhas[nome]
                st.download_button(
                    label="[📤] Exportar para Excel",
                    data=to_excel(df_export),
                    file_name=f"{nome}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                   )
