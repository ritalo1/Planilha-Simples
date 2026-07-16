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

    mostrar_kpis = st.checkbox("Mostrar KPIs básicos", value=True)
    mostrar_kpis_avancados = st.checkbox("Mostrar KPIs avançados", value=True)
    mostrar_graficos = st.checkbox("Mostrar gráficos", value=True)

    st.markdown("---")
    st.markdown("### Criar nova planilha")
    novo_nome = st.text_input("Nome da nova planilha (ex: Fevereiro)")
    if st.button("Adicionar planilha"):
        if novo_nome.strip() != "":
            st.session_state.planilhas[novo_nome] = pd.DataFrame(MODELO)
            st.success(f"Planilha '{novo_nome}' criada com sucesso!")

# ============================
# CONTEÚDO PRINCIPAL
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:

        df = st.session_state.planilhas[nome]

        # Conversão de tipos
        df["Descrição"] = df["Descrição"].astype(str)
        df["Categoria"] = df["Categoria"].astype(str)
        df["Observações"] = df["Observações"].astype(str)
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

        # ============================
        # DASHBOARD
        # ============================

        if pagina == "Dashboard":

            st.markdown(f"<h2 style='color:#4CAF50;'>📊 Dashboard — {nome}</h2>", unsafe_allow_html=True)

            df_kpi = df.copy()
            df_kpi["Valor"] = pd.to_numeric(df_kpi["Valor"], errors="coerce").fillna(0)

            # KPIs básicos
            if mostrar_kpis:
                st.subheader("📌 Indicadores do mês")

                total = df_kpi["Valor"].sum()
                media = df_kpi["Valor"].mean()
                maior = df_kpi["Valor"].max()
                qtd = len(df_kpi)

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total gasto", f"R$ {total:,.2f}")
                col2.metric("Média por gasto", f"R$ {media:,.2f}")
                col3.metric("Maior gasto", f"R$ {maior:,.2f}")
                col4.metric("Nº de transações", qtd)

            # KPIs avançados
            if mostrar_kpis_avancados and not df_kpi.empty:
                st.divider()
                st.subheader("📊 KPIs avançados")

                # Total por categoria + percentual
                df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                st.write("Total por categoria")
                st.dataframe(df_cat)

                # Ticket médio por categoria
                df_ticket = df_kpi.groupby("Categoria", as_index=False)["Valor"].mean()
                df_ticket.rename(columns={"Valor": "Ticket Médio"}, inplace=True)
                st.write("Ticket médio por categoria")
                st.dataframe(df_ticket)

                # Dia com maior gasto
                df_data = df_kpi.dropna(subset=["Data"])
                if not df_data.empty:
                    dia_max = df_data.loc[df_data["Valor"].idxmax()]
                    st.info(
                        f"📅 Dia com maior gasto: {dia_max['Data'].date()} — R$ {dia_max['Valor']:,.2f}"
                    )

                # Gráfico de pizza
                grafico_pizza = alt.Chart(df_cat).mark_arc().encode(
                    theta="Valor",
                    color="Categoria",
                    tooltip=["Categoria", "Valor", "Percentual"]
                )
                st.subheader("🍕 Distribuição por categoria")
                st.altair_chart(grafico_pizza, use_container_width=True)

            # Gráficos principais
            if mostrar_graficos:
                st.divider()

                st.subheader("📊 Gastos por categoria")
                if not df.empty:
                    grafico_cat = alt.Chart(df).mark_bar(
                        cornerRadiusTopLeft=5,
                        cornerRadiusTopRight=5
                    ).encode(
                        x=alt.X("Categoria", sort="-y"),
                        y="Valor",
                        color="Categoria"
                    ).properties(height=300)

                    st.altair_chart(grafico_cat, use_container_width=True)

                st.subheader("📈 Gastos ao longo do mês")
                df_data = df.dropna(subset=["Data"])
                if not df_data.empty:
                    grafico_tempo = alt.Chart(df_data).mark_line(
                        color="#4CAF50",
                        strokeWidth=3
                    ).encode(
                        x="Data",
                        y="Valor"
                    ).properties(height=300)

                    st.altair_chart(grafico_tempo, use_container_width=True)

        # ============================
        # PLANILHAS
        # ============================

        elif pagina == "Planilhas":

            st.markdown(f"<h2 style='color:#4CAF50;'>🧾 Planilha — {nome}</h2>", unsafe_allow_html=True)

            # Importar Excel
            st.subheader("📥 Importar planilha Excel")
            arquivo = st.file_uploader("Selecione um arquivo .xlsx", type=["xlsx"], key=f"upload_{nome}")

            if arquivo:
                df_importado = pd.read_excel(arquivo)

                # Normaliza nomes das colunas
                df_importado.columns = df_importado.columns.str.strip().str.title()

                # Garante colunas esperadas
                colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
                for col in colunas_esperadas:
                    if col not in df_importado.columns:
                        df_importado[col] = None

                st.session_state.planilhas[nome] = df_importado
                st.success("Planilha importada com sucesso!")

            # Editor
            df = st.session_state.planilhas[nome]

            st.session_state.planilhas[nome] = st.data_editor(
                df,
                num_rows="dynamic",
                key=f"editor_{nome}",
                use_container_width=True,
                column_config={
                    "Descrição": st.column_config.TextColumn("Descrição"),
                    "Categoria": st.column_config.SelectboxColumn(
                        "Categoria",
                        options=CATEGORIAS
                    ),
                    "Data": st.column_config.DateColumn("Data"),
                    "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "Observações": st.column_config.TextColumn("Observações")
                }
            )

            # Total
            if st.button(f"Calcular total de {nome}"):
                df_calc = st.session_state.planilhas[nome].copy()
                df_calc["Valor"] = pd.to_numeric(df_calc["Valor"], errors="coerce").fillna(0)
                total = df_calc["Valor"].sum()
                st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")
                st.dataframe(df_calc)

            # Exportar Excel
            st.subheader("📤 Exportar planilha")
            df_export = st.session_state.planilhas[nome]

            st.download_button(
                label="📤 Exportar para Excel",
                data=to_excel(df_export),
                file_name=f"{nome}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )CATEGORIAS = [
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

    mostrar_kpis = st.checkbox("Mostrar KPIs básicos", value=True)
    mostrar_kpis_avancados = st.checkbox("Mostrar KPIs avançados", value=True)
    mostrar_graficos = st.checkbox("Mostrar gráficos", value=True)

    st.markdown("---")
    st.markdown("### Criar nova planilha")
    novo_nome = st.text_input("Nome da nova planilha (ex: Fevereiro)")
    if st.button("Adicionar planilha"):
        if novo_nome.strip() != "":
            st.session_state.planilhas[novo_nome] = pd.DataFrame(MODELO)
            st.success(f"Planilha '{novo_nome}' criada com sucesso!")

# ============================
# CONTEÚDO PRINCIPAL
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:

        df = st.session_state.planilhas[nome]

        # Conversão de tipos
        df["Descrição"] = df["Descrição"].astype(str)
        df["Categoria"] = df["Categoria"].astype(str)
        df["Observações"] = df["Observações"].astype(str)
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

        # ============================
        # DASHBOARD
        # ============================

        if pagina == "Dashboard":

            st.markdown(f"<h2 style='color:#4CAF50;'>📊 Dashboard — {nome}</h2>", unsafe_allow_html=True)

            df_kpi = df.copy()
            df_kpi["Valor"] = pd.to_numeric(df_kpi["Valor"], errors="coerce").fillna(0)

            # KPIs básicos
            if mostrar_kpis:
                st.subheader("📌 Indicadores do mês")

                total = df_kpi["Valor"].sum()
                media = df_kpi["Valor"].mean()
                maior = df_kpi["Valor"].max()
                qtd = len(df_kpi)

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total gasto", f"R$ {total:,.2f}")
                col2.metric("Média por gasto", f"R$ {media:,.2f}")
                col3.metric("Maior gasto", f"R$ {maior:,.2f}")
                col4.metric("Nº de transações", qtd)

            # KPIs avançados
            if mostrar_kpis_avancados and not df_kpi.empty:
                st.divider()
                st.subheader("📊 KPIs avançados")

                # Total por categoria + percentual
                df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                st.write("Total por categoria")
                st.dataframe(df_cat)

                # Ticket médio por categoria
                df_ticket = df_kpi.groupby("Categoria", as_index=False)["Valor"].mean()
                df_ticket.rename(columns={"Valor": "Ticket Médio"}, inplace=True)
                st.write("Ticket médio por categoria")
                st.dataframe(df_ticket)

                # Dia com maior gasto
                df_data = df_kpi.dropna(subset=["Data"])
                if not df_data.empty:
                    dia_max = df_data.loc[df_data["Valor"].idxmax()]
                    st.info(
                        f"📅 Dia com maior gasto: {dia_max['Data'].date()} — R$ {dia_max['Valor']:,.2f}"
                    )

                # Gráfico de pizza
                grafico_pizza = alt.Chart(df_cat).mark_arc().encode(
                    theta="Valor",
                    color="Categoria",
                    tooltip=["Categoria", "Valor", "Percentual"]
                )
                st.subheader("🍕 Distribuição por categoria")
                st.altair_chart(grafico_pizza, use_container_width=True)

            # Gráficos principais
            if mostrar_graficos:
                st.divider()

                st.subheader("📊 Gastos por categoria")
                if not df.empty:
                    grafico_cat = alt.Chart(df).mark_bar(
                        cornerRadiusTopLeft=5,
                        cornerRadiusTopRight=5
                    ).encode(
                        x=alt.X("Categoria", sort="-y"),
                        y="Valor",
                        color="Categoria"
                    ).properties(height=300)

                    st.altair_chart(grafico_cat, use_container_width=True)

                st.subheader("📈 Gastos ao longo do mês")
                df_data = df.dropna(subset=["Data"])
                if not df_data.empty:
                    grafico_tempo = alt.Chart(df_data).mark_line(
                        color="#4CAF50",
                        strokeWidth=3
                    ).encode(
                        x="Data",
                        y="Valor"
                    ).properties(height=300)

                    st.altair_chart(grafico_tempo, use_container_width=True)

        # ============================
        # PLANILHAS
        # ============================

        elif pagina == "Planilhas":

            st.markdown(f"<h2 style='color:#4CAF50;'>🧾 Planilha — {nome}</h2>", unsafe_allow_html=True)

            # Importar Excel
            st.subheader("📥 Importar planilha Excel")
            arquivo = st.file_uploader("Selecione um arquivo .xlsx", type=["xlsx"], key=f"upload_{nome}")

            if arquivo:
                df_importado = pd.read_excel(arquivo)

                # Normaliza nomes das colunas
                df_importado.columns = df_importado.columns.str.strip().str.title()

                # Garante colunas esperadas
                colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
                for col in colunas_esperadas:
                    if col not in df_importado.columns:
                        df_importado[col] = None

                st.session_state.planilhas[nome] = df_importado
                st.success("Planilha importada com sucesso!")

            # Editor
            df = st.session_state.planilhas[nome]

            st.session_state.planilhas[nome] = st.data_editor(
                df,
                num_rows="dynamic",
                key=f"editor_{nome}",
                use_container_width=True,
                column_config={
                    "Descrição": st.column_config.TextColumn("Descrição"),
                    "Categoria": st.column_config.SelectboxColumn(
                        "Categoria",
                        options=CATEGORIAS
                    ),
                    "Data": st.column_config.DateColumn("Data"),
                    "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "Observações": st.column_config.TextColumn("Observações")
                }
            )

            # Total
            if st.button(f"Calcular total de {nome}"):
                df_calc = st.session_state.planilhas[nome].copy()
                df_calc["Valor"] = pd.to_numeric(df_calc["Valor"], errors="coerce").fillna(0)
                total = df_calc["Valor"].sum()
                st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")
                st.dataframe(df_calc)

            # Exportar Excel
            st.subheader("📤 Exportar planilha")
            df_export = st.session_state.planilhas[nome]

            st.download_button(
                label="📤 Exportar para Excel",
                data=to_excel(df_export),
                file_name=f"{nome}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
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

    mostrar_kpis = st.checkbox("Mostrar KPIs básicos", value=True)
    mostrar_kpis_avancados = st.checkbox("Mostrar KPIs avançados", value=True)
    mostrar_graficos = st.checkbox("Mostrar gráficos", value=True)

    st.markdown("---")
    st.markdown("### Criar nova planilha")
    novo_nome = st.text_input("Nome da nova planilha (ex: Fevereiro)")
    if st.button("Adicionar planilha"):
        if novo_nome.strip() != "":
            st.session_state.planilhas[novo_nome] = pd.DataFrame(MODELO)
            st.success(f"Planilha '{novo_nome}' criada com sucesso!")

# ============================
# CONTEÚDO PRINCIPAL
# ============================

abas = st.tabs(list(st.session_state.planilhas.keys()))

for nome, aba in zip(st.session_state.planilhas.keys(), abas):
    with aba:

        df = st.session_state.planilhas[nome]

        # Conversão de tipos
        df["Descrição"] = df["Descrição"].astype(str)
        df["Categoria"] = df["Categoria"].astype(str)
        df["Observações"] = df["Observações"].astype(str)
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

        # ============================
        # DASHBOARD
        # ============================

        if pagina == "Dashboard":

            st.markdown(f"<h2 style='color:#4CAF50;'>📊 Dashboard — {nome}</h2>", unsafe_allow_html=True)

            df_kpi = df.copy()
            df_kpi["Valor"] = pd.to_numeric(df_kpi["Valor"], errors="coerce").fillna(0)

            # KPIs básicos
            if mostrar_kpis:
                st.subheader("📌 Indicadores do mês")

                total = df_kpi["Valor"].sum()
                media = df_kpi["Valor"].mean()
                maior = df_kpi["Valor"].max()
                qtd = len(df_kpi)

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total gasto", f"R$ {total:,.2f}")
                col2.metric("Média por gasto", f"R$ {media:,.2f}")
                col3.metric("Maior gasto", f"R$ {maior:,.2f}")
                col4.metric("Nº de transações", qtd)

            # KPIs avançados
            if mostrar_kpis_avancados and not df_kpi.empty:
                st.divider()
                st.subheader("📊 KPIs avançados")

                # Total por categoria + percentual
                df_cat = df_kpi.groupby("Categoria", as_index=False)["Valor"].sum()
                df_cat["Percentual"] = (df_cat["Valor"] / df_cat["Valor"].sum()) * 100
                st.write("Total por categoria")
                st.dataframe(df_cat)

                # Ticket médio por categoria
                df_ticket = df_kpi.groupby("Categoria", as_index=False)["Valor"].mean()
                df_ticket.rename(columns={"Valor": "Ticket Médio"}, inplace=True)
                st.write("Ticket médio por categoria")
                st.dataframe(df_ticket)

                # Dia com maior gasto
                df_data = df_kpi.dropna(subset=["Data"])
                if not df_data.empty:
                    dia_max = df_data.loc[df_data["Valor"].idxmax()]
                    st.info(
                        f"📅 Dia com maior gasto: {dia_max['Data'].date()} — R$ {dia_max['Valor']:,.2f}"
                    )

                # Gráfico de pizza
                grafico_pizza = alt.Chart(df_cat).mark_arc().encode(
                    theta="Valor",
                    color="Categoria",
                    tooltip=["Categoria", "Valor", "Percentual"]
                )
                st.subheader("🍕 Distribuição por categoria")
                st.altair_chart(grafico_pizza, use_container_width=True)

            # Gráficos principais
            if mostrar_graficos:
                st.divider()

                st.subheader("📊 Gastos por categoria")
                if not df.empty:
                    grafico_cat = alt.Chart(df).mark_bar(
                        cornerRadiusTopLeft=5,
                        cornerRadiusTopRight=5
                    ).encode(
                        x=alt.X("Categoria", sort="-y"),
                        y="Valor",
                        color="Categoria"
                    ).properties(height=300)

                    st.altair_chart(grafico_cat, use_container_width=True)

                st.subheader("📈 Gastos ao longo do mês")
                df_data = df.dropna(subset=["Data"])
                if not df_data.empty:
                    grafico_tempo = alt.Chart(df_data).mark_line(
                        color="#4CAF50",
                        strokeWidth=3
                    ).encode(
                        x="Data",
                        y="Valor"
                    ).properties(height=300)

                    st.altair_chart(grafico_tempo, use_container_width=True)

        elif pagina == "Planilhas":

    st.markdown(f"<h2 style='color:#4CAF50;'>🧾 Planilha — {nome}</h2>", unsafe_allow_html=True)

    # Importar Excel
    st.subheader("📥 Importar planilha Excel")
    arquivo = st.file_uploader("Selecione um arquivo .xlsx", type=["xlsx"], key=f"upload_{nome}")

    if arquivo:
        df_importado = pd.read_excel(arquivo)

        # Normaliza nomes das colunas
        df_importado.columns = df_importado.columns.str.strip().str.title()

        # Garante colunas esperadas
        colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
        for col in colunas_esperadas:
            if col not in df_importado.columns:
                df_importado[col] = None

        st.session_state.planilhas[nome] = df_importado
        st.success("Planilha importada com sucesso!")

    # ============================
    # EDITOR (sempre fora do if)
    # ============================

    df = st.session_state.planilhas[nome]

    st.session_state.planilhas[nome] = st.data_editor(
        df,
        num_rows="dynamic",
        key=f"editor_{nome}",
        use_container_width=True,
        column_config={
            "Descrição": st.column_config.TextColumn("Descrição"),
            "Categoria": st.column_config.SelectboxColumn(
                "Categoria",
                options=CATEGORIAS
            ),
            "Data": st.column_config.DateColumn("Data"),
            "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "Observações": st.column_config.TextColumn("Observações")
        }
    )

    # ============================
    # TOTAL
    # ============================

    if st.button(f"Calcular total de {nome}"):
        df_calc = st.session_state.planilhas[nome].copy()
        df_calc["Valor"] = pd.to_numeric(df_calc["Valor"], errors="coerce").fillna(0)
        total = df_calc["Valor"].sum()
        st.success(f"Total de gastos em {nome}: R$ {total:,.2f}")
        st.dataframe(df_calc)

    # ============================
    # EXPORTAR
    # ============================

    st.subheader("📤 Exportar planilha")
    df_export = st.session_state.planilhas[nome]

    st.download_button(
        label="📤 Exportar para Excel",
        data=to_excel(df_export),
        file_name=f"{nome}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
