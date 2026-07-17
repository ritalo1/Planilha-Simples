import pandas as pd
import streamlit as st

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

@st.cache_data(show_spinner=False)
def limpar_planilha(df):
    linhas_antes = len(df)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)].copy()
    df.columns = df.columns.str.strip().str.title()

    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Descrição: só limpar espaços, nunca apagar conteúdo
    df["Descrição"] = df["Descrição"].astype(str).str.strip()

    # Categoria: normalizar e corrigir inválidas
    df["Categoria"] = df["Categoria"].astype(str).str.strip()
    df.loc[~df["Categoria"].isin(CATEGORIAS), "Categoria"] = "Outros"

    # Observações: preservar texto, só limpar espaços
    df["Observações"] = df["Observações"].astype(str).str.strip()

    # Data: conversão segura
    if isinstance(df["Data"], pd.DataFrame):
        df["Data"] = df["Data"].iloc[:, 0]

    df["Data"] = df["Data"].apply(
        lambda x: x if isinstance(x, (str, pd.Timestamp)) else None
    )

    try:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    except Exception:
        st.warning("⚠️ A coluna 'Data' contém valores inválidos. Mantendo valores originais.")
        df["Data"] = df["Data"].astype(str)

    # Valor: conversão segura
    def limpar_valor(v):
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            v = v.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            try:
                return float(v)
            except:
                return None
        return None

    df["Valor"] = df["Valor"].apply(limpar_valor)
    valores_nulos_corrigidos = df["Valor"].isna().sum()
    df["Valor"] = df["Valor"].fillna(0.0)

    df = df.dropna(how="all")

    st.success(
        f"🧹 ETL concluído: {len(df)} linhas (antes: {linhas_antes}), "
        f"{valores_nulos_corrigidos} valores nulos corrigidos."
    )

    return df[colunas_esperadas]
