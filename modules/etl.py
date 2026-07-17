import pandas as pd
import streamlit as st

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

@st.cache_data(show_spinner=False)
def limpar_planilha(df):
    linhas_antes = len(df)

    # Remove colunas Unnamed
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)]

    # Remove linhas totalmente vazias
    df = df.dropna(how="all")

    # Padroniza nomes das colunas
    df.columns = df.columns.str.strip().str.title()

    # Garante que todas as colunas esperadas existam
    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Limpeza básica
    df["Descrição"] = df["Descrição"].fillna("").astype(str).str.strip()
    df["Categoria"] = df["Categoria"].fillna("Outros").astype(str).str.strip()
    df["Observações"] = df["Observações"].fillna("").astype(str).str.strip()

    # ============================
    # CORREÇÃO DA COLUNA DE DATA
    # ============================

    # Se a coluna "Data" vier como DataFrame (erro comum no Streamlit), pega só a primeira coluna
    if isinstance(df["Data"], pd.DataFrame):
        df["Data"] = df["Data"].iloc[:, 0]

    # Se vier como lista de dicts ou algo estranho, converte para string antes
    if df["Data"].apply(lambda x: isinstance(x, dict)).any():
        df["Data"] = df["Data"].astype(str)

    # Conversão segura
    try:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    except Exception:
        st.warning("⚠️ A coluna 'Data' contém valores inválidos. Mantendo valores originais.")
        # Mantém como string para não quebrar o app
        df["Data"] = df["Data"].astype(str)

    # ============================
    # CORREÇÃO DA COLUNA DE VALOR
    # ============================

    if not df["Valor"].empty:
        df["Valor"] = (
            df["Valor"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    valores_nulos_corrigidos = df["Valor"].isna().sum()
    df["Valor"] = df["Valor"].fillna(0.0)

    # ============================
    # CATEGORIAS INVÁLIDAS
    # ============================

    categorias_validas = set(CATEGORIAS)
    inconsistentes = (~df["Categoria"].isin(categorias_validas)).sum()
    df.loc[~df["Categoria"].isin(categorias_validas), "Categoria"] = "Outros"

    # ============================
    # FEEDBACK DO ETL
    # ============================

    st.success(
        f"🧹 ETL concluído: {len(df)} linhas (antes: {linhas_antes}), "
        f"{valores_nulos_corrigidos} valores nulos corrigidos, "
        f"{inconsistentes} categorias ajustadas."
    )

    return df[colunas_esperadas]
