import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

# ============================
# FUNÇÃO PARA EXPORTAR EXCEL
# ============================

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, index=False, sheet_name="Gastos")
    writer.close()
    return output.getvalue()

# ============================
# CABEÇALHO MODERNO
# ============================

st.markdown(
    """
    <h1 style='text-align: center; color: #4CAF50;'>
        💸 Sistema de Gastos Mensais
    </h1>
    <p style='text-align: center; color: #CCCCCC;'>
        Organize seus gastos, visualize gráficos e acompanhe indicadores.
    </p>
    """,
    unsafe_allow_html=True
)

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

# ============================
# INICIALIZAÇÃO
# ============================

if "planilhas" not in st.session_state:
    st.session_state.planilhas = {
        "Janeiro": pd.DataFrame(MODELO)
    }

# ============================
# MENU LATERAL
# ============================

with st.sidebar:
    st.markdown("## ⚙️ Menu")

    pagina = st.radio(
        "Escolha a página",
        ["Dashboard", "Planilhas"]
    )

    # ============================
    # KPIs (pai)
    # ============================

    mostrar_kpis = st.checkbox("📊 Mostrar KPIs", value=True)

    if mostrar_kpis:
        st.markdown("##### Tipos de KPIs")

        kpi_genericos = st.checkbox("KPIs genéricos (alfanuméricos)", value=True)
        kpi_total_categoria = st.checkbox("Total por categoria", value=True)
        kpi_ticket_medio = st.checkbox("Ticket médio por categoria", value=True)
        kpi_dia_max = st.checkbox("Dia com maior gasto", value=True)

    # ============================
    # Gráficos (pai)
    # ============================

    mostrar_graficos = st.checkbox("📈 Mostrar gráficos", value=True)

    if mostrar_graficos:
        st.markdown("##### Tipos de gráficos")

        grafico_generico = st.checkbox("Gráfico genérico (frequência)", value=True)
        grafico_pizza = st.checkbox("Gráfico de pizza", value=True)
        grafico_barras = st.checkbox("Gráfico de barras", value=True)
        grafico_linha = st.checkbox("Linha ao longo do mês", value=True)

    st.markdown("---")
    st.markdown("### Criar nova planilha")
    novo_nome = st.text_input("Nome da nova planilha (ex: Fevereiro)")
    if st.button("Adicionar planilha"):
        if novo_nome.strip() != "":
            st.session_state.planilhas[novo_nome] = pd.DataFrame(MODELO)
            st.success(f"Planilha '{novo_nome}' criada com sucesso!")

# ============================
# FUNÇÕES DE KPIs E GRÁFICOS
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

def grafico_barras_generico(df, coluna):
    freq = df[coluna].value_counts().reset_index()
    freq.columns = [coluna, "Frequência"]

    grafico = alt.Chart(freq).mark_bar().encode(
        x=alt.X(coluna, type="nominal"),
        y=alt.Y("Frequência:Q"),
        color=alt.Color(coluna, type="nominal")
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

def grafico_barras(df):
    grafico = alt.Chart(df).mark_bar(
        cornerRadiusTopLeft=5,
        cornerRadiusTopRight=5
    ).encode(
        x=alt.X("Categoria", sort="-y"),
        y="Valor",
        color="Categoria"
    )
    st.subheader("📊 Gastos por categoria")
    st.altair_chart(grafico, use_container_width=True)

def grafico_linha(df):
    df_data = df.dropna(subset=["Data"])
    grafico = alt.Chart(df_data).mark_line(
        color="#4CAF50",
        strokeWidth=3
    ).encode(
        x="Data",
        y="Valor"
    )
    st.subheader("📈 Gastos ao longo do mês")
    st.altair_chart(grafico, use_container_width=True)

# ============================
# CONTEÚDO PRINCIPAL
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:

        df = st.session_state.planilhas[nome]

        # Remove colunas Unnamed automaticamente
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        df["Descrição"] = df["Descrição"].astype(str)
        df["Categoria"] = df["Categoria"].astype(str)
        df["Observações"] = df["Observações"].astype(str)
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

        # Atualiza opções da sidebar
        st.sidebar.selectbox("Escolha a coluna para KPIs", df.columns, key=f"kpi_col_{nome}")
        st.sidebar.selectbox("Escolha a coluna para gráficos", df.columns, key=f"graf_col_{nome}")

        # ============================
        # DASHBOARD
        # ============================

        if pagina == "Dashboard":

            st.markdown(f"<h2 style='color:#4CAF50;'>📊 Dashboard — {nome}</h2>", unsafe_allow_html=True)

            df_kpi = df.copy()
            df_kpi["Valor"] = pd.to_numeric(df_kpi["Valor"], errors="coerce").fillna(0)

            coluna_kpi = st.session_state[f"kpi_col_{nome}"]
            coluna_grafico = st.session_state[f"graf_col_{nome}"]

            # KPIs genéricos
            if mostrar_kpis and kpi_genericos and coluna_kpi in df.columns:
                kpi_valores_unicos(df, coluna_kpi)
                kpi_frequencia(df, coluna_kpi)
                kpi_mais_comum(df, coluna_kpi)

            # KPIs específicos
            if mostrar_kpis:
                if kpi_total_categoria:
