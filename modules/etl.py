import pandas as pd
import streamlit as st

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

@st.cache_data(show_spinner=False)
def limpar_planilha(df):
    linhas_antes = len(df)

    # Remove colunas Unnamed, mas não mexe em conteúdo válido
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)].copy()

    # Padroniza nomes das colunas sem alterar dados
    df.columns = df.columns.str.strip().str.title()

    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Descrição: só strip, nunca apagar conteúdo
    df["Descrição"] = df["Descrição"].astype(str).str.strip()

    # Categoria: normaliza e corrige apenas inválidas
    df["Categoria"] = df["Categoria"].astype(str).str.strip()
    df.loc[~df["Categoria"].isin(CATEGORIAS), "Categoria"] = "Outros"

    # Observações: só strip
    df["Observações"] = df["Observações"].astype(str).str.strip()

    # Data: só converte strings plausíveis, preserva timestamps
    def trata_data(x):
        if isinstance(x, pd.Timestamp):
            return x
        if isinstance(x, str) and x.strip():
            try:
                return pd.to_datetime(x, errors="raise")
            except Exception:
                return x
        return None

    df["Data"] = df["Data"].apply(trata_data)

    # Valor: só converte se claramente numérico
    def limpar_valor(v):
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str) and v.strip():
            raw = v.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            try:
                return float(raw)
            except Exception:
                return v  # preserva texto inválido
        return None

    df["Valor"] = df["Valor"].apply(limpar_valor)

    # Não força zero em tudo: só preenche nulos numéricos
    mask_num = df["Valor"].apply(lambda x: isinstance(x, (int, float, float)))
    valores_nulos_corrigidos = df["Valor"].isna().sum()
    df.loc[mask_num & df["Valor"].isna(), "Valor"] = 0.0

    df = df.dropna(how="all")

    st.success(
        f"🧹 ETL concluído: {len(df)} linhas (antes: {linhas_antes}), "
        f"{valores_nulos_corrigidos} valores nulos numéricos corrigidos."
    )

    return df[colunas_esperadas]
