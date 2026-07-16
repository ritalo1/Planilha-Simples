import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

# ============================
# CONFIGURAÇÃO GLOBAL
# ============================

st.set_page_config(
    page_title="Sistema de Gastos Mensais",
    page_icon="💸",
    layout="wide"
)

# ============================
# FUNÇÕES UTILITÁRIAS
# ============================

@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gastos")
    return output.getvalue()

def limpar_planilha(df):
    linhas_antes = len(df)
    categorias_inconsistentes = 0
    valores_nulos_corrigidos = 0

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
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    # Corrige valores nulos
    valores_nulos_corrigidos = df["Valor"].isna().sum()
    df["Valor"] = df["Valor"].fillna(0)

    # Trata categorias inválidas
    categorias_validas = set(CATEGORIAS)
    categorias_inconsistentes = (~df["Categoria"].isin(categorias_validas)).sum()
    df.loc[~df["Categoria"].isin(categorias_validas), "Categoria"] = "Outros"

    # Log de auditoria
    linhas_depois = len(df)
    st.success(
        f"ETL concluído: {linhas_depois} linhas processadas "
        f"(antes: {linhas_antes}), "
        f"{valores_nulos_corrigidos} valores nulos corrigidos, "
        f"{categorias_inconsistentes} categorias mapeadas para 'Outros'."
    )

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
    st.subheader("📊 Frequência")
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

def kpi_outliers(df_filtrado):
    if df_filtrado.empty:
        return
    media_valor = df_filtrado["Valor"].mean()
    desvio_padrao = df_filtrado["Valor"].std()
    limite_outlier = media_valor + (2 * desvio_padrao)

    outliers = df_filtrado[df_filtrado["Valor"] > limite_outlier]

    if not outliers.empty:
        st.warning(
            f"⚠️ Detectamos {len(outliers)} gasto(s) anormalmente alto(s) "
            f"(acima de R$ {limite_outlier:,.2f}):"
        )
        st.dataframe(outliers[["Descrição", "Categoria", "Valor", "Data"]])
    else:
        st.success("✅ Nenhum gasto discrepante (outlier) detectado.")

def kpi_orcamento(df_kpi, meta_orcamento):
    total = df_kpi["Valor"].sum()
    if meta_orcamento <= 0:
        st.info("Defina uma meta de orçamento maior que zero para acompanhar o uso.")
        return
    percentual_gasto = (total / meta_orcamento) * 100
    st.markdown(
        f"**Uso do Orçamento: {percentual_gasto:.1f}% de R$ {meta_orcamento:,.2f}**"
    )
    st.progress(min(percentual_gasto / 100, 1.0))
    if percentual_gasto > 100:
        st.error(f"🚨 Orçamento estourado em R$ {total - meta_orcamento:,.2f}!")

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

    st.subheader("📊 Frequência (barras)")
    st.altair_chart(grafico, use_container_width=True)

def grafico_pizza(df_cat):
    grafico = alt.Chart(df_cat).mark_arc().encode(
        theta="Valor",
        color="Categoria",
        tooltip=["Categoria", "Valor", "Percentual"]
    )
    st.subheader("🍕 Distribuição por categoria (pizza)")
    st.altair_chart(grafico, use_container_width=True)

def grafico_donut(df_cat):
    grafico = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
        theta="Valor",
        color="Categoria",
        tooltip=["Categoria", "Valor", "Percentual"]
    )
    st.subheader("🍩 Distribuição por categoria (donut)")
    st.altair_chart(grafico, use_container_width=True)

def grafico_treemap(df_cat):
    grafico = alt.Chart(df_cat).mark_rect().encode(
        x=alt.X("Categoria:N", axis=None),
        y=alt.Y("Valor:Q", axis=None),
        color="Categoria",
        tooltip=["Categoria", "Valor", "Percentual"]
    )
    st.subheader("🧱 Treemap simplificado por categoria")
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
    st.subheader("📊 Gastos por categoria (barras)")
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
    st.subheader("📈 Gastos ao longo do tempo (linha)")
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

    # Paleta de cores
    st.markdown("**[🎨] Cor dos gráficos**")
    paleta = {
        "Verde": "#4CAF50",
        "Verde escuro": "#2E7D32",
        "Azul": "#2196F3",
        "Azul claro": "#64B5F6",
        "Roxo": "#9C27B0",
        "Rosa": "#E91E63",
        "Laranja": "#FB8C00",
        "Cinza": "#BDBDBD"
    }
    nome_cor = st.selectbox("Escolha a cor principal", list(paleta.keys()))
    st.session_state.cor_grafico = paleta[nome_cor]

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
            destacar_outliers = st.checkbox("🔍 Destacar anomalias (Outliers)", value=False)
            meta_orcamento = st.number_input(
                "🎯 Meta de Orçamento Máximo (R$)",
                min_value=0.0,
                value=3000.0
            )

        st.markdown("---")

        # Switch Gráficos
        mostrar_graficos = st.checkbox("[📈] Mostrar gráficos", value=True)
        if mostrar_graficos:
            st.markdown("**[🧩] Tipos de gráficos**")
            grafico_generico_on = st.checkbox("Gráfico genérico (frequência)", value=True)
            grafico_pizza_on = st.checkbox("Gráfico de pizza", value=False)
            grafico_donut_on = st.checkbox("Gráfico de donut", value=True)
            grafico_treemap_on = st.checkbox("Treemap por categoria", value=False)
            grafico_barras_on = st.checkbox("Gráfico de barras", value=True)
            grafico_linha_on = st.checkbox("Gráfico de linha", value=True)
            grafico_histograma_on = st.checkbox("Histograma de valores", value=False)
            grafico_boxplot_on = st.checkbox("Boxplot por categoria", value=False)

        st.markdown("---")

        # Filtros avançados
        filtros_on = st.checkbox("[🔎] Filtros avançados", value=False)
        if filtros_on:
            st.markdown("**Filtros**")
            st.session_state.filtros_texto = st.text_input("Buscar na descrição", "")

        st.markdown("---")

    elif pagina == "Planilhas":
        st.markdown("**[📄] Criar nova planilha**")
        novo_nome = st.text_input("Nome da nova planilha (ex: Fevereiro)")
        if st.button("[➕] Adicionar planilha"):
            if novo_nome.strip() != "":
                if novo_nome in st.session_state.planilhas:
                    st.error("Já existe uma planilha com esse nome.")
                else:
                    st.session_state.planilhas[novo_nome] = pd.DataFrame(MODELO)
                    st.success(f"Planilha '{novo_nome}' criada com sucesso!")
        st.markdown("---")
        st.markdown("Use a aba de cada mês para importar, limpar, editar e exportar.")

# ============================
# CONTEÚDO PRINCIPAL
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:
        df = st.session_state.planilhas[nome]

        if pagina == "Dashboard":
            st.markdown(f"<h2 style='color:#4CAF50;'>📊 Dashboard — {nome}</h2>", unsafe_allow_html=True)

            if df.empty:
                st.warning("Planilha vazia. Vá na aba Planilhas e preencha os dados.")
                continue

            # Seleção de colunas para KPIs e gráficos
            coluna_kpi = st.selectbox("Coluna para KPIs", df.columns, key=f"kpi_col_{nome}")
            coluna_grafico = st.selectbox("Coluna para gráfico genérico", df.columns, key=f"graf_col_{nome}")

            # Filtros avançados (com base no df)
            data_min = df["Data"].min() if not df["Data"].isna().all() else pd.to_datetime("2024-01-01")
            data_max = df["Data"].max() if not df["Data"].isna().all() else pd.to_datetime("2024-12-31")
            valor_min_default = float(df["Valor"].min()) if not df["Valor"].isna().all() else 0.0
            valor_max_default = float(df["Valor"].max()) if not df["Valor"].isna().all() else 1000.0

            if filtros_on:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    data_ini = st.date_input("Data inicial", data_min, key=f"data_ini_{nome}")
                    vmin = st.number_input("Valor mínimo", value=valor_min_default, key=f"vmin_{nome}")
                with col_f2:
                    data_fim = st.date_input("Data final", data_max, key=f"data_fim_{nome}")
                    vmax = st.number_input("Valor máximo", value=valor_max_default, key=f"vmax_{nome}")

                categorias_sel = st.multiselect(
                    "Categorias",
                    options=df["Categoria"].unique(),
                    key=f"cats_{nome}"
                )

                df_filtrado = aplicar_filtros(
                    df,
                    True,
                    categorias_sel,
                    data_ini,
                    data_fim,
                    vmin,
                    vmax,
                    st.session_state.filtros_texto
                )
            else:
                df_filtrado = df.copy()

            df_kpi = df_filtrado.copy()
            cor = st.session_state.cor_grafico

            # KPIs
            if mostrar_kpis:
                if kpi_genericos and coluna_kpi in df_filtrado.columns:
                    kpi_valores_unicos(df_filtrado, coluna_kpi)
                    kpi_frequencia(df_filtrado, coluna_kpi)
                    kpi_mais_comum(df_filtrado, coluna_kpi)

                if kpi_total_categoria_on:
                    df_cat = kpi_total_categoria(df_kpi)

                if kpi_ticket_medio_on:
                    kpi_ticket_medio(df_kpi)

                if kpi_dia_max_on:
                    kpi_dia_max(df_kpi)

                if destacar_outliers:
                    kpi_outliers(df_filtrado)

                kpi_orcamento(df_kpi, meta_orcamento)

            # Gráficos
            if mostrar_graficos:
                if grafico_generico_on and coluna_grafico in df_filtrado.columns:
                    grafico_barras_generico(df_filtrado, coluna_grafico, cor)

                if grafico_pizza_on:
                    df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                    df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                    grafico_pizza(df_cat)

                if grafico_donut_on:
                    df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                    df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                    grafico_donut(df_cat)

                if grafico_treemap_on:
                    df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                    df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                    grafico_treemap(df_cat)

                if grafico_barras_on:
                    grafico_barras(df_kpi, cor)

                if grafico_linha_on:
                    grafico_linha(df_kpi, cor)

                if grafico_histograma_on:
                    grafico_histograma(df_kpi, cor)

                if grafico_boxplot_on:
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

                st.info("Mapeie as colunas do arquivo para o padrão do sistema:")

                colunas_detectadas = list(df_importado.columns)

                col_desc = st.selectbox("Coluna de Descrição", colunas_detectadas, key=f"map_desc_{nome}")
                col_cat = st.selectbox("Coluna de Categoria", colunas_detectadas, key=f"map_cat_{nome}")
                col_val = st.selectbox("Coluna de Valor", colunas_detectadas, key=f"map_val_{nome}")
                col_data = st.selectbox("Coluna de Data", colunas_detectadas, key=f"map_data_{nome}")

                if st.button("Confirmar mapeamento e limpar", key=f"map_btn_{nome}"):
                    df_importado = df_importado.rename(columns={
                        col_desc: "Descrição",
                        col_cat: "Categoria",
                        col_val: "Valor",
                        col_data: "Data"
                    })
                    df_importado = limpar_planilha(df_importado)
                    st.session_state.planilhas[nome] = df_importado
                    df = df_importado
                    st.success("Planilha importada, mapeada e limpa com sucesso!")

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
                    df_calc = st.session_state.planilhas[nome].copy()
                    df_calc = limpar_planilha(df_calc)
                    total = df_calc["Valor"].sum()
                    st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")
                    st.dataframe(df_calc)

            with col_b3:
                df_export = st.session_state.planilhas[nome]
                st.download_button(
                    label="[📤] Exportar para Excel",
                    data=to_excel(df_export),
                    file_name=f"{nome}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
