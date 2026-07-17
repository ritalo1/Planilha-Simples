import pandas as pd
import streamlit as st

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

def limpar_planilha(df):
    df = df.copy()

    # Padroniza nomes das colunas
    df.columns = df.columns.str.strip().str.title()

    # Garante colunas esperadas
    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Tratamento célula por célula
    for linha in df.index:
        for coluna in df.columns:
            valor = df.at[linha, coluna]

            # DESCRIÇÃO
            if coluna == "Descrição":
                df.at[linha, coluna] = "" if valor is None else str(valor).strip()

            # CATEGORIA
            elif coluna == "Categoria":
                texto = str(valor).strip() if valor else "Outros"
                df.at[linha, coluna] = texto if texto in CATEGORIAS else "Outros"

            # DATA
            elif coluna == "Data":
                if isinstance(valor, pd.Timestamp):
                    continue
                if isinstance(valor, str) and valor.strip():
                    try:
                        df.at[linha, coluna] = pd.to_datetime(valor, errors="raise")
                    except:
                        df.at[linha, coluna] = valor
                else:
                    df.at[linha, coluna] = None

            # VALOR
            elif coluna == "Valor":
                if isinstance(valor, (int, float)):
                    continue
                if isinstance(valor, str) and valor.strip():
                    raw = valor.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                    try:
                        df.at[linha, coluna] = float(raw)
                    except:
                        df.at[linha, coluna] = 0.1
                else:
                    df.at[linha, coluna] = 0.1

            # OBSERVAÇÕES
            elif coluna == "Observações":
                df.at[linha, coluna] = "" if valor is None else str(valor).strip()

    # Organiza por categoria
    df = df.sort_values(by="Categoria")

    st.success("🧹 Planilha limpa e organizada por categoria.")

    return df[colunas_esperadas] 
