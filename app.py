import streamlit as st
from modules.interface import render_header, render_sidebar
from modules.dashboard import render_dashboard
from modules.planilhas import render_planilhas
from modules.console_sql import render_console_sql
from modules.utils import aplicar_filtros

render_header()
pagina = render_sidebar()

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:
        df = st.session_state.planilhas[nome]

        if pagina == "Dashboard":
            st.write("Chamar dashboard aqui")

        elif pagina == "Planilhas":
            render_planilhas(df, nome)

        elif pagina == "Console SQL":
            render_console_sql(df, nome)})

if "planilhas" not in st.session_state:
    st.session_state.planilhas = {"Janeiro": MODELO.copy()}

if "cor_grafico" not in st.session_state:
    st.session_state.cor_grafico = "#4CAF50"

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

    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)]
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip().str.title()

    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    df["Descrição"] = df["Descrição"].fillna("").astype(str).str.strip()
    df["Categoria"] = df["Categoria"].fillna("Outros").astype(str).str.strip()
    df["Observações"] = df["Observações"].fillna("").astype(str).str.strip()

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

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

    categorias_validas = set(CATEGORIAS)
    categorias_inconsistentes = (~df["Categoria"].isin(categorias_validas)).sum()
    df.loc[~df["Categoria"].isin(categorias_validas), "Categoria"] = "Outros"

    st.success(
        f"🧹 ETL concluído: {len(df)} linhas (antes: {linhas_antes}), "
        f"{valores_nulos_corrigidos} valores nulos corrigidos, "
        f"{categorias_inconsistentes} categorias mapeadas para 'Outros'."
    )

    return df[colunas_esperadas]

def aplicar_filtros(df, filtros_on, categorias_sel, data_ini, data_fim, vmin, vmax, texto):
    if not filtros_on or df.empty:
        return df

    df_filtrado = df.copy()

    if categorias_sel:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias_sel)]

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
# CABEÇALHO
# ============================

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #4CAF50; margin-bottom: 5px;'>💸 Sistema de Gastos PRO</h1>
        <p style='color: #BBBBBB; font-size: 14px;'>Dashboard, ETL e Console SQL — tudo em um só lugar.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================
# SIDEBAR
# ============================

with st.sidebar:
    st.markdown("## ⚙️ Navegação")

    pagina = st.radio(
        "Escolha a página:",
        ["Dashboard", "Console SQL", "Planilhas"]
    )

    st.markdown("---")

    st.markdown("### 🎨 Tema e cores")
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
    nome_cor = st.selectbox("Cor principal dos gráficos", list(paleta.keys()))
    st.session_state.cor_grafico = paleta[nome_cor]

    st.markdown("---")

    if pagina == "Dashboard":
        st.markdown("### 📊 Indicadores")
        mostrar_kpis = st.checkbox("Mostrar KPIs", value=True)
        kpi_genericos = st.checkbox("KPIs genéricos (frequência)", value=True)
        kpi_total_categoria_on = st.checkbox("Total por categoria", value=True)
        kpi_ticket_medio_on = st.checkbox("Ticket médio", value=True)
        kpi_dia_max_on = st.checkbox("Dia de maior gasto", value=True)
        destacar_outliers = st.checkbox("🔍 Destacar outliers", value=False)

        st.markdown("### 🎯 Orçamento")
        meta_orcamento = st.number_input(
            "Meta mensal (R$)",
            min_value=0.0,
            value=3000.0,
            step=100.0
        )

        st.markdown("### 📈 Gráficos")
        mostrar_graficos = st.checkbox("Mostrar gráficos", value=True)
        grafico_donut_on = st.checkbox("Donut por categoria", value=True)
        grafico_barras_on = st.checkbox("Barras por categoria", value=True)
        grafico_linha_on = st.checkbox("Linha do tempo", value=True)
        grafico_histograma_on = st.checkbox("Histograma", value=False)
        grafico_boxplot_on = st.checkbox("Boxplot", value=False)

        st.markdown("### 🔎 Filtros")
        filtros_on = st.checkbox("Ativar filtros avançados", value=False)

    elif pagina == "Planilhas":
        st.markdown("### 📂 Nova planilha")
        novo_nome = st.text_input("Nome do mês (ex: Fevereiro)")
        if st.button("➕ Criar planilha"):
            if novo_nome.strip():
                nome_formatado = novo_nome.strip()
                if nome_formatado in st.session_state.planilhas:
                    st.error("Já existe uma planilha com esse nome.")
                else:
                    st.session_state.planilhas[nome_formatado] = MODELO.copy()
                    st.success(f"Planilha '{nome_formatado}' criada.")
                    st.rerun()

    elif pagina == "Console SQL":
        st.markdown("### 🗄️ Tabelas disponíveis")
        for nome_mês in st.session_state.planilhas.keys():
            st.code(f"df_{nome_mês.lower()}", language="sql")

# ============================
# TABS POR PLANILHA
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:
        df = st.session_state.planilhas[nome]

        # ============================
        # DASHBOARD
        # ============================
        if pagina == "Dashboard":
            st.markdown(
                f"<h3 style='color:#4CAF50;'>📊 Dashboard — {nome}</h3>",
                unsafe_allow_html=True
            )

            if df.empty:
                st.warning("Planilha vazia. Vá em 'Planilhas' para importar ou editar dados.")
                continue

            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                coluna_kpi = st.selectbox(
                    "Coluna para KPIs de frequência",
                    df.columns,
                    key=f"kpi_col_{nome}"
                )
            with col_sel2:
                coluna_graf_generico = st.selectbox(
                    "Coluna para análise genérica",
                    df.columns,
                    key=f"graf_col_{nome}"
                )

            if filtros_on:
                st.markdown("#### 🔎 Filtros avançados")
                col_f1, col_f2 = st.columns(2)

                data_min = df["Data"].min() if not df["Data"].isna().all() else pd.to_datetime("2024-01-01")
                data_max = df["Data"].max() if not df["Data"].isna().all() else pd.to_datetime("2024-12-31")
                valor_min_default = float(df["Valor"].min()) if not df["Valor"].isna().all() else 0.0
                valor_max_default = float(df["Valor"].max()) if not df["Valor"].isna().all() else 1000.0

                with col_f1:
                    categorias_sel = st.multiselect(
                        "Categorias",
                        options=CATEGORIAS,
                        key=f"cats_{nome}"
                    )
                    data_ini = st.date_input(
                        "Data inicial",
                        data_min,
                        key=f"data_ini_{nome}"
                    )
                    vmin = st.number_input(
                        "Valor mínimo (R$)",
                        value=valor_min_default,
                        key=f"vmin_{nome}"
                    )
                with col_f2:
                    texto_filtro = st.text_input(
                        "Buscar na descrição",
                        "",
                        key=f"txt_{nome}"
                    )
                    data_fim = st.date_input(
                        "Data final",
                        data_max,
                        key=f"data_fim_{nome}"
                    )
                    vmax = st.number_input(
                        "Valor máximo (R$)",
                        value=valor_max_default,
                        key=f"vmax_{nome}"
                    )

                df_filtrado = aplicar_filtros(
                    df, True, categorias_sel, data_ini, data_fim, vmin, vmax, texto_filtro
                )
            else:
                df_filtrado = df.copy()

            df_kpi = df_filtrado.copy()
            cor = st.session_state.cor_grafico

            if mostrar_kpis and not df_filtrado.empty:
                st.markdown("#### 📌 Indicadores")

                if meta_orcamento > 0:
                    total_gastos = df_filtrado["Valor"].sum()
                    percentual_gasto = (total_gastos / meta_orcamento) * 100
                    st.markdown(
                        f"**Uso do orçamento: {percentual_gasto:.1f}% de R$ {meta_orcamento:,.2f}**"
                    )
                    st.progress(min(percentual_gasto / 100, 1.0))
                    if percentual_gasto > 100:
                        st.error(f"🚨 Orçamento estourado em R$ {total_gastos - meta_orcamento:,.2f}!")

                if kpi_genericos:
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Total de lançamentos", len(df_filtrado))
                    with col_m2:
                        st.metric("Valores únicos", df_filtrado[coluna_kpi].nunique())
                    with col_m3:
                        modo = df_filtrado[coluna_kpi].mode()
                        st.metric(
                            "Valor mais frequente",
                            str(modo.iloc[0]) if not modo.empty else "N/A"
                        )

                df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100

                if kpi_total_categoria_on:
                    st.markdown("**💰 Total por categoria**")
                    df_cat_fmt = df_cat.copy()
                    df_cat_fmt["Valor"] = df_cat_fmt["Valor"].map("R$ {:,.2f}".format)
                    df_cat_fmt["Percentual"] = df_cat_fmt["Percentual"].map("{:.1f}%".format)
                    st.dataframe(df_cat_fmt, use_container_width=True)

                if kpi_ticket_medio_on:
                    st.markdown("**💳 Ticket médio por categoria**")
                    df_ticket = df_kpi.groupby("Categoria", as_index=False)["Valor"].mean()
                    df_ticket.columns = ["Categoria", "Ticket médio (R$)"]
                    df_ticket["Ticket médio (R$)"] = df_ticket["Ticket médio (R$)"].map("R$ {:,.2f}".format)
                    st.dataframe(df_ticket, use_container_width=True)

                if kpi_dia_max_on:
                    df_data_valida = df_kpi.dropna(subset=["Data"])
                    if not df_data_valida.empty:
                        dia_max = df_data_valida.loc[df_data_valida["Valor"].idxmax()]
                        st.info(
                            f"📅 Maior gasto em {dia_max['Data'].strftime('%d/%m/%Y')} "
                            f"no valor de R$ {dia_max['Valor']:,.2f} ({dia_max['Descrição']})."
                        )

                if destacar_outliers and len(df_filtrado) > 1:
                    media_valor = df_filtrado["Valor"].mean()
                    desvio_padrao = df_filtrado["Valor"].std()
                    limite_outlier = media_valor + (2 * desvio_padrao)
                    outliers = df_filtrado[df_filtrado["Valor"] > limite_outlier]
                    if not outliers.empty:
                        st.warning(
                            f"⚠️ {len(outliers)} lançamento(s) acima de R$ {limite_outlier:,.2f}:"
                        )
                        st.dataframe(
                            outliers[["Descrição", "Categoria", "Valor", "Data"]],
                            use_container_width=True
                        )
                    else:
                        st.success("✅ Nenhum outlier detectado.")

            if mostrar_graficos and not df_filtrado.empty:
                st.markdown("#### 📊 Gráficos")

                if grafico_donut_on:
                    graf_donut = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
                        theta="Valor:Q",
                        color="Categoria:N",
                        tooltip=["Categoria", "Valor", "Percentual"]
                    ).properties(height=300)
                    st.subheader("🍩 Distribuição por categoria (donut)")
                    st.altair_chart(graf_donut, use_container_width=True)

                if grafico_barras_on:
                    graf_bar = alt.Chart(df_cat).mark_bar(
                        cornerRadiusTopLeft=5,
                        cornerRadiusTopRight=5,
                        color=cor
                    ).encode(
                        x=alt.X("Categoria:N", sort="-y", title="Categoria"),
                        y=alt.Y("Valor:Q", title="Total (R$)")
                    ).properties(height=300)
                    st.subheader("📊 Total por categoria (barras)")
                    st.altair_chart(graf_bar, use_container_width=True)

                if grafico_linha_on:
                    df_linha = df_kpi.dropna(subset=["Data"])
                    if not df_linha.empty:
                        graf_line = alt.Chart(df_linha).mark_line(
                            color=cor,
                            strokeWidth=3
                        ).encode(
                            x=alt.X("Data:T", title="Data"),
                            y=alt.Y("Valor:Q", title="Valor (R$)")
                        ).properties(height=300)
                        st.subheader("📈 Gastos ao longo do tempo")
                        st.altair_chart(graf_line, use_container_width=True)

                if grafico_histograma_on:
                    graf_hist = alt.Chart(df_kpi).mark_bar(color=cor).encode(
                        x=alt.X("Valor:Q", bin=alt.Bin(maxbins=20), title="Faixa de valores"),
                        y=alt.Y("count()", title="Frequência")
                    ).properties(height=250)
                    st.subheader("📊 Histograma de valores")
                    st.altair_chart(graf_hist, use_container_width=True)

                if grafico_boxplot_on:
                    graf_box = alt.Chart(df_kpi).mark_boxplot().encode(
                        x=alt.X("Categoria:N", title="Categoria"),
                        y=alt.Y("Valor:Q", title="Valor (R$)")
                    ).properties(height=300)
                    st.subheader("📦 Boxplot por categoria")
                    st.altair_chart(graf_box, use_container_width=True)

        # ============================
        # PLANILHAS
        # ============================
        elif pagina == "Planilhas":
           st.markdown(
             f"<h3 style='color:#4CAF50;'>🧾 Planilha — {nome}</h3>",
             unsafe_allow_html=True
           )

           st.subheader("📥 Importar planilha")
           arquivo = st.file_uploader(
             "Selecione um arquivo",
             type=["xlsx", "xlsm", "ods", "csv", "tsv"],
             key=f"upload_{nome}"
           )

           if arquivo:
               nome_arquivo = arquivo.name.lower()

           if nome_arquivo.endswith((".csv", ".tsv")):
               df_importado = pd.read_csv(arquivo)
           else:
               df_importado = pd.read_excel(arquivo, engine="openpyxl")

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

           st.subheader("✏️ Editar dados")
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
               if st.button(f"🧹 Limpar planilha — {nome}"):
                   df_limpo = limpar_planilha(st.session_state.planilhas[nome])
                   st.session_state.planilhas[nome] = df_limpo
                   st.success("Planilha limpa.")
                   st.dataframe(df_limpo, use_container_width=True)

           with col_b2:
               if st.button(f"🧮 Calcular total — {nome}"):
                   df_calc = limpar_planilha(st.session_state.planilhas[nome].copy())
                   total = df_calc["Valor"].sum()
                   st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")
                   st.dataframe(df_calc, use_container_width=True)

           with col_b3:
               df_export = st.session_state.planilhas[nome]
               st.download_button(
                   label="📤 Exportar para Excel",
                   data=to_excel(df_export),
                   file_name=f"{nome}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
               )

        # ============================
        # CONSOLE SQL
        # ============================
        elif pagina == "Console SQL":
            st.markdown(
                f"<h3 style='color:#4CAF50;'>💻 Console SQL — {nome}</h3>",
                unsafe_allow_html=True
            )

            for mes_db, df_db in st.session_state.planilhas.items():
                globals()[f"df_{mes_db.lower()}"] = df_db

            query_padrao = (
                f"SELECT Categoria, SUM(Valor) AS total_gasto\n"
                f"FROM df_{nome.lower()}\n"
                f"GROUP BY Categoria\n"
                f"ORDER BY total_gasto DESC"
            )

            sql_query = st.text_area(
                "Escreva sua consulta SQL (DuckDB):",
                value=query_padrao,
                height=140,
                help="Use df_<nomedomes>, ex: SELECT * FROM df_janeiro"
            )

            if st.button("⚡ Executar SQL", key=f"run_sql_{nome}"):
                try:
                    resultado_df = duckdb.query(sql_query).to_df()
                    st.success("Query executada com sucesso.")

                    col_res1, col_res2 = st.columns(2)

                    with col_res1:
                        st.markdown("#### 📋 Resultado")
                        st.dataframe(resultado_df, use_container_width=True)
                        st.download_button(
                            label="📥 Baixar resultado em Excel",
                            data=to_excel(resultado_df),
                            file_name=f"resultado_sql_{nome.lower()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_sql_{nome}"
                        )

                    with col_res2:
                        st.markdown("#### 📊 Gráfico automático")
                        colunas_retornadas = list(resultado_df.columns)
                        if len(colunas_retornadas) >= 2:
                            x_axis = colunas_retornadas[0]
                            y_axis = colunas_retornadas[1]
                            st.info(f"Visualização: {x_axis} x {y_axis}")

                            grafico_auto = alt.Chart(resultado_df).mark_bar(
                                color=st.session_state.cor_grafico,
                                cornerRadiusTopLeft=5,
                                cornerRadiusTopRight=5
                            ).encode(
                                x=alt.X(x_axis, sort="-y", title=x_axis),
                                y=alt.Y(y_axis, title=y_axis),
                                tooltip=colunas_retornadas
                            ).properties(height=280)

                            st.altair_chart(grafico_auto, use_container_width=True)
                        else:
                            st.warning("Retorne pelo menos 2 colunas para gerar gráfico.")
                except Exception as error:
                    st.error(f"Erro ao executar SQL: {error}")
                     
