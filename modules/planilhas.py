import pandas as pd
import streamlit as st

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

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
            df["Valor"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    valores_nulos_corrigidos = df["Valor"].isna().sum()
    df["Valor"] = df["Valor"].fillna(0.0)

    categorias_validas = set(CATEGORIAS)
    inconsistentes = (~df["Categoria"].isin(categorias_validas)).sum()
    df.loc[~df["Categoria"].isin(categorias_validas), "Categoria"] = "Outros"

    st.success(
        f"🧹 ETL concluído: {len(df)} linhas (antes: {linhas_antes}), "
        f"{valores_nulos_corrigidos} valores nulos corrigidos, "
        f"{inconsistentes} categorias ajustadas."
    )

    return df[colunas_esperadas]
