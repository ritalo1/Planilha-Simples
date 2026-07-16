import streamlit as st
import pandas as pd
import altair as alt
import duckdb
from io import BytesIO

# ============================
# CONFIGURAÇÃO GLOBAL E LAYOUT
# ============================

st.set_page_config(
    page_title="Sistema de Gastos SQL Pro",
    page_icon="💸",
    layout="wide"
)

# ============================
# CONSTANTES E MODELOS
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

MODELO = pd.DataFrame({
    "Descrição": pd.Series(dtype='str'),
    "Categoria": pd.Series(dtype='str'),
    "Data": pd.Series(dtype='datetime64[ns]'),
    "Valor": pd.Series(dtype='float'),
    "Observações": pd.Series(dtype='str')
})

# Inicialização do estado da sessão
if "planilhas" not in st.session_state:
    st.session_state.planilhas = {
        "Janeiro": MODELO.copy()
    }

if "cor_grafico" not in st.session_state:
    st.session_state.cor_grafico = "#4CAF50"

# ============================
# FUNÇÕES UTILITÁRIAS & ETL
# ============================

@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gastos")
    return output.getvalue()

def limpar_planilha(df):
    linhas_antes = len(df)
    
    # Remove colunas Unnamed geradas pelo Excel/CSV
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)]

    # Remove linhas totalmente vazias
    df = df.dropna(how="all")

    # Padroniza colunas (Títulos)
    df.columns = df.columns.str.strip().str.title()

    # Garante a existência das colunas esperadas do modelo
    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Preenche vazios e converte tipos básicos
    df["Descrição"] = df["Descrição"].fillna("").astype(str).str.strip()
    df["Categoria"] = df["Categoria"].fillna("Outros").astype(str).str.strip()
    df["Observações"] = df["Observações"].fillna("").astype(str).str.strip()

    # Tratamento de datas
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Tratamento robusto de moedas e formatos numéricos
    if not df["Valor"].empty:
        df["Valor"] = (
            df["Valor"]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    
    valores_nulos_corrigidos = df["Valor"].isna().sum()
    df["Valor"] = df["Valor"].fillna(0.0)

    # Garante que categorias inválidas sejam convertidas para "Outros"
    categorias_validas = set(CATEGORIAS)
    categorias_inconsistentes = (~df["Categoria"].isin(categorias_validas)).sum()
    df.loc[~df["Categoria"].isin(categorias_validas), "Categoria"] = "Outros"

    # Log de auditoria inteligente
    st.success(
        f"🧹 ETL concluído com sucesso: {len(df)} linhas processadas (antes: {linhas_antes}). "
        f"Foram corrigidos {valores_nulos_corrigidos} valores nulos e "
        f"{categorias_inconsistentes} categorias inconsistentes mapeadas para 'Outros'."
    )

    return df[colunas_esperadas]

def aplicar_filtros(df, filtros_on, categorias_sel, data_ini, data_fim, vmin, vmax, texto):
    if not filtros_on or df.empty:
        return df

    df_filtrado = df.copy()

    if categorias_sel:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias_sel)]

    # Tratamento preventivo para datas nulas nos filtros
    if not df_filtrado["Data"].isna().all():
        df_filtrado = df_filtrado[
            (df_filtrado["Data"] >= pd.to_datetime(data_ini)) &
            (df_filtrado["Data"] <= pd.to_datetime(data_fim))
        ]

    df_filtrado = df_filtrado[
        (df_filtrado["Valor"] >= vmin) &
        (df_filtrado["Valor"] <= vmax)
    ]

    if texto.strip():
        df_filtrado = df_filtrado[
            df_filtrado["Descrição"].str.contains(texto, case=False, na=False)
        ]

    return df_filtrado

# ============================
# CABEÇALHO DO SISTEMA
# ============================

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #4CAF50; margin-bottom: 5px;'>💸 Sistema de Gastos SQL Pro</h1>
        <p style='color: #888888; font-size: 14px;'>Engine Analítica Integrada — Powered by DuckDB & Altair</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================
# SIDEBAR INTELIGENTE
# ============================

with st.sidebar:
    st.markdown("## ⚙️ Menu de Navegação")

    pagina = st.radio(
        "Ir para a página:",
        ["Dashboard", "Console SQL", "Planilhas"]
    )

    st.markdown("---")

    # Mapeador de tabelas ativas no Data Lake local
    st.markdown("### 🗄️ Tabelas Ativas (SQL)")
    for nome_mês in st.session_state.planilhas.keys():
        st.code(f"df_{nome_mês.lower()}", language="sql")

    st.markdown("---")

    if pagina == "Dashboard":
        # Paleta de cores
        st.markdown("**🎨 Estilização**")
        paleta = {
            "Verde Esmeralda": "#4CAF50",
            "Azul Corporativo": "#2196F3",
            "Roxo Moderno": "#9C27B0",
            "Laranja Intenso": "#FB8C00",
            "Vermelho Alerta": "#E91E63"
        }
        nome_cor = st.selectbox("Cor principal dos gráficos", list(paleta.keys()))
        st.session_state.cor_grafico = paleta[nome_cor]

        st.markdown("---")

        # Configurações de KPIs
        mostrar_kpis = st.checkbox("📊 Mostrar Indicadores", value=True)
        if mostrar_kpis:
            st.markdown("**Métricas Ativas:**")
            kpi_genericos = st.checkbox("Frequência de coluna", value=True)
            kpi_total_categoria_on = st.checkbox("Total consolidado", value=True)
            kpi_ticket_medio_on = st.checkbox("Ticket médio por categoria", value=True)
            kpi_dia_max_on = st.checkbox("Pico de gasto diário", value=True)
            destacar_outliers = st.checkbox("🔍 Destacar Outliers", value=False)
            
            st.markdown("---")
            st.markdown("**🎯 Gestão de Orçamento**")
            meta_orcamento = st.number_input(
                "Limite mensal de gastos (R$)",
                min_value=0.0,
                value=5000.0,
                step=500.0
            )

        st.markdown("---")

        # Configurações de Gráficos
        mostrar_graficos = st.checkbox("📈 Mostrar Gráficos", value=True)
        if mostrar_graficos:
            st.markdown("**Tipos de Visualização:**")
            grafico_donut_on = st.checkbox("Donut (Distribuição)", value=True)
            grafico_barras_on = st.checkbox("Barras por Categoria", value=True)
            grafico_linha_on = st.checkbox("Linha do Tempo", value=True)
            grafico_histograma_on = st.checkbox("Histograma de Frequência", value=False)
            grafico_boxplot_on = st.checkbox("Boxplot (Dispersão)", value=False)

        st.markdown("---")
        filtros_on = st.checkbox("🔎 Ativar Filtros Rápidos", value=False)

    elif pagina == "Planilhas":
        st.markdown("### 📂 Adicionar Mês/Tabela")
        novo_nome = st.text_input("Nome do mês (ex: Fevereiro)")
        if st.button("➕ Adicionar Planilha"):
            if novo_nome.strip():
                nome_formatado = novo_nome.strip()
                if nome_formatado in st.session_state.planilhas:
                    st.error("Uma planilha com este nome já existe.")
                else:
                    st.session_state.planilhas[nome_formatado] = MODELO.copy()
                    st.success(f"Tabela '{nome_formatado}' criada com sucesso!")
                    st.rerun()

# ============================
# CONTEÚDO PRINCIPAL (TABS)
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:
        df = st.session_state.planilhas[nome]

        # ==========================================
        # PÁGINA: DASHBOARD (LEITURA E ANÁLISE)
        # ==========================================
        if pagina == "Dashboard":
            st.markdown(f"<h3 style='color:#4CAF50;'>📊 Dashboard — {nome}</h3>", unsafe_allow_html=True)

            if df.empty:
                st.warning("💡 Tabela vazia! Vá até a aba 'Planilhas' para importar ou adicionar novos dados.")
                continue

            # --- SEÇÃO BUDGET TRACKER ---
            if mostrar_kpis and meta_orcamento > 0:
                total_gastos = df["Valor"].sum()
                percentual_gasto = (total_gastos / meta_orcamento) * 100
                
                st.markdown(f"**Uso do Orçamento Mensal: {percentual_gasto:.1f}% de R$ {meta_orcamento:,.2f}**")
                if percentual_gasto > 100:
                    st.progress(1.0)
                    st.error(f"🚨 Orçamento estourado em R$ {total_gastos - meta_orcamento:,.2f}!")
                else:
                    st.progress(percentual_gasto / 100)
                st.divider()

            # Configurações de colunas para análise genérica
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                coluna_kpi = st.selectbox("Selecione a coluna para métricas de frequência:", df.columns, key=f"kpi_col_{nome}")
            with col_sel2:
                coluna_graf_generico = st.selectbox("Selecione a coluna para análise gráfica:", df.columns, key=f"graf_col_{nome}")

            # --- PROCESSAMENTO FILTROS ---
            if filtros_on:
                st.markdown("#### 🔎 Painel de Filtros Avançados")
                col_f1, col_f2 = st.columns(2)
                
                data_min = df["Data"].min() if not df["Data"].isna().all() else pd.to_datetime("2026-01-01")
                data_max = df["Data"].max() if not df["Data"].isna().all() else pd.to_datetime("2026-12-31")
                valor_min_default = float(df["Valor"].min()) if not df["Valor"].isna().all() else 0.0
                valor_max_default = float(df["Valor"].max()) if not df["Valor"].isna().all() else 1000.0

                with col_f1:
                    categorias_sel = st.multiselect("Filtrar por Categorias", options=CATEGORIAS, key=f"cats_{nome}")
                    data_ini = st.date_input("Data Inicial", data_min, key=f"data_ini_{nome}")
                    vmin = st.number_input("Valor Mínimo (R$)", value=valor_min_default, key=f"vmin_{nome}")
                with col_f2:
                    texto_filtro = st.text_input("Pesquisar na Descrição", "", key=f"txt_{nome}")
                    data_fim = st.date_input("Data Final", data_max, key=f"data_fim_{nome}")
                    vmax = st.number_input("Valor Máximo (R$)", value=valor_max_default, key=f"vmax_{nome}")

                df_filtrado = aplicar_filtros(df, True, categorias_sel, data_ini, data_fim, vmin, vmax, texto_filtro)
            else:
                df_filtrado = df.copy()

            df_kpi = df_filtrado.copy()
            cor = st.session_state.cor_grafico

            # --- DETECTOR DE OUTLIERS ---
            if mostrar_kpis and destacar_outliers and not df_filtrado.empty and len(df_filtrado) > 1:
                media_valor = df_filtrado["Valor"].mean()
                desvio_padrao = df_filtrado["Valor"].std()
                limite_outlier = media_valor + (2 * desvio_padrao)

                outliers = df_filtrado[df_filtrado["Valor"] > limite_outlier]
                if not outliers.empty:
                    st.warning(f"⚠️ Identificamos {len(outliers)} lançamento(s) discrepante(s) (gastos acima de R$ {limite_outlier:,.2f}):")
                    st.dataframe(outliers[["Descrição", "Categoria", "Valor", "Data"]], use_container_width=True)
                else:
                    st.success("✅ Nenhum desvio incomum de gastos detectado no mês.")

            # --- RENDERIZAÇÃO KPIs ---
            if mostrar_kpis and not df_filtrado.empty:
                st.markdown("#### 📌 Indicadores Corporativos")
                
                if kpi_genericos:
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Total de Lançamentos", len(df_filtrado))
                    with col_m2:
                        st.metric("Itens Únicos", df_filtrado[coluna_kpi].nunique())
                    with col_m3:
                        modo = df_filtrado[coluna_kpi].mode()
                        st.metric("Valor Mais Frequente", str(modo.iloc[0]) if not modo.empty else "N/A")

                df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100

                if kpi_total_categoria_on:
                    st.markdown("**💰 Total Acumulado por Categoria**")
                    df_cat_fmt = df_cat.copy()
                    df_cat_fmt["Valor"] = df_cat_fmt["Valor"].map("R$ {:,.2f}".format)
                    df_cat_fmt["Percentual"] = df_cat_fmt["Percentual"].map("{:.1f}%".format)
                    st.dataframe(df_cat_fmt, use_container_width=True)

                if kpi_ticket_medio_on:
                    st.markdown("**💳 Ticket Médio das Transações**")
                    df_ticket = df_kpi.groupby("Categoria", as_index=False)["Valor"].mean()
                    df_ticket.columns = ["Categoria", "Ticket Médio (R$)"]
                    df_ticket["Ticket Médio (R$)"] = df_ticket["Ticket Médio (R$)"].map("R$ {:,.2f}".format)
                    st.dataframe(df_ticket, use_container_width=True)

                if kpi_dia_max_on:
                    df_data_valida = df_kpi.dropna(subset=["Data"])
                    if not df_data_valida.empty:
                        dia_max = df_data_valida.loc[df_data_valida["Valor"].idxmax()]
                        st.info(f"📅 Gasto pico registrado em **{dia_max['Data'].strftime('%d/%m/%Y')}** no valor de **R$ {dia_max['Valor']:,.2f}** ({dia_max['Descrição']}).")

            # --- RENDERIZAÇÃO GRÁFICOS ---
            if mostrar_graficos and not df_filtrado.empty:
                st.divider()
                st.markdown("#### 📊 Distribuição Visual de Gastos")

                if grafico_donut_on:
                    graf_donut = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
                        theta="Valor:Q",
                        color="Categoria:N",
                        tooltip=["Categoria", "Valor"]
                    ).properties(height=300)
                    st.subheader("🍩 Proporção por Categoria (Donut Chart)")
                    st.altair_chart(graf_donut, use_container_width=True)

                if grafico_barras_on:
                    graf_bar = alt.Chart(df_cat).mark_bar(
                        cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color=cor
                    ).encode(
                        x=alt.X("Categoria", sort="-y", title="Categoria"),
                        y=alt.Y("Valor", title="Total Financeiro (R$)")
                    ).properties(height=300)
                    st.subheader("📊 Faturamento/Gasto Total por Categoria")
                    st.altair_chart(graf_bar, use_container_width=True)

                if grafico_linha_on:
                    df_linha = df_kpi.dropna(subset=["Data"])
                    if not df_linha.empty:
                        graf_line = alt.Chart(df_linha).mark_line(
                            color=cor, strokeWidth=3
                        ).encode(
                            x=alt.X("Data:T", title="Linha do Tempo"),
                            y=alt.Y("Valor:Q", title="Valor do Lançamento (R$)")
                        ).properties(height=300)
                        st.subheader("📈 Histórico Cronológico de Gastos")
                        st.altair_chart(graf_line, use_container_width=True)

                if grafico_histograma_on:
                    graf_hist = alt.Chart(df_kpi).mark_bar(color=cor).encode(
                        x=alt.X("Valor:Q", bin=alt.Bin(maxbins=20), title="Faixa de Preços (Bins)"),
                        y=alt.Y("count()", title="Frequência")
                    ).properties(height=250)
                    st.subheader("📊 Distribuição de Frequência de Preços")
                    st.altair_chart(graf_hist, use_container_width=True)

                if grafico_boxplot_on:
                    graf_box = alt.Chart(df_kpi).mark_boxplot().encode(
                        x=alt.X("Categoria:N", title="Categoria"),
                        y=alt.Y("Valor:Q", title="Dispersão de Valores")
                    ).properties(height=300)
                    st.subheader("📦 Dispersão Estatística (Boxplot)")
                    st.altair_chart(graf_box, use_container_width=True)

        # ==========================================
        # PÁGINA: CONSOLE SQL (ENGINE ANALÍTICA)
        # ==========================================
        elif pagina == "Console SQL":
            st.markdown(f"<h3 style='color:#4CAF50;'>💻 Console SQL DuckDB — {nome}</h3>", unsafe_allow_html=True)
            
            # Disponibiliza todos os DataFrames no escopo global para que o DuckDB os encontre
            for mes_db, df_db in st.session_state.planilhas.items():
                globals()[f"df_{mes_db.lower()}"] = df_db

            # Cria uma query padrão baseada no mês atual da Tab
            query_padrao = (
                f"SELECT Categoria, SUM(Valor) as total_gasto\n"
                f"FROM df_{nome.lower()}\n"
                f"GROUP BY Categoria\n"
                f"ORDER BY total_gasto DESC"
            )

            sql_query = st.text_area(
                "Escreva sua Consulta SQL padrão ANSI:",
                value=query_padrao,
                height=140,
                help="Sempre consulte utilizando o prefixo: df_<nomedomes>. Ex: SELECT * FROM df_janeiro"
            )

            if st.button("⚡ Executar Consulta SQL", key=f"run_sql_{nome}", type="primary"):
                try:
                    # DuckDB lê diretamente do DataFrame local em tempo recorde!
                    resultado_df = duckdb.query(sql_query).to_df()
                    
                    st.success("Query executada com sucesso!")
                    
                    col_res1, col_res2 = st.columns(2)
                    
                    with col_res1:
                        st.markdown("#### 📋 Dataset Retornado")
                        st.dataframe(resultado_df, use_container_width=True)
                        
                        st.download_button(
                            label="📥 Baixar resultado em Excel",
                            data=to_excel(resultado_df),
                            file_name=f"resultado_query_sql_{nome.lower()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_sql_{nome}"
                        )
                        
                    with col_res2:
                        st.markdown("#### 📊 Análise Gráfica Automatizada")
                        colunas_retornadas = list(resultado_df.columns)
                        
                        if len(colunas_retornadas) >= 2:
                            x_axis = colunas_retornadas[0]
                            y_axis = colunas_retornadas[1]
                            
                            st.info(f"Visualização gerada para: **{x_axis}** x **{y_axis}**")
                            
                            # Ajuste e fechamento corretos dos parênteses do Altair
                            grafico_auto = alt.Chart(resultado_df).mark_bar(
                                color="#4CAF50", 
                  
