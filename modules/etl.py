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
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)].copy()

    # Padroniza nomes das colunas
    df.columns = df.columns.str.strip().str.title()

    # Garante colunas esperadas
    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Tratamento célula por célula (estilo Excel)
    for linha in df.index:
        for coluna in df.columns:

            valor = df.at[linha, coluna]

            # ============================
            # DESCRIÇÃO
            # ============================
            if coluna == "Descrição":
                if valor is None:
                    df.at[linha, coluna] = ""
                else:
                    df.at[linha, coluna] = str(valor).strip()

            # ============================
            # CATEGORIA
            # ============================
            elif coluna == "Categoria":
                if valor is None or str(valor).strip() == "":
                    df.at[linha, coluna] = "Outros"
                else:
                    texto = str(valor).strip()
                    df.at[linha, coluna] = texto if texto in CATEGORIAS else "Outros"

            # ============================
            # DATA
            # ============================
            elif coluna == "Data":
                if isinstance(valor, pd.Timestamp):
                    continue
                if isinstance(valor, str) and valor.strip():
                    try:
                        df.at[linha, coluna] = pd.to_datetime(valor, errors="raise")
                    except:
                        df.at[linha, coluna] = valor  # preserva texto
                else:
                    df.at[linha, coluna] = None

            # ============================
            # VALOR
            # ============================
            elif coluna == "Valor":
                if isinstance(valor, (int, float)):
                    continue
                if isinstance(valor, str) and valor.strip():
                    raw = valor.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                    try:
                        df.at[linha, coluna] = float(raw)
                    except:
                        df.at[linha, coluna] = 0.1  # qualquer caractere vira 0.1
                else:
                    df.at[linha, coluna] = 0.1

            # ============================
            # OBSERVAÇÕES
            # ============================
            elif coluna == "Observações":
                if valor is None:
                    df.at[linha, coluna] = ""
                else:
                    df.at[linha, coluna] = str(valor).strip()

    st.success(
        f"🧹 ETL concluído: {len(df)} linhas (antes: {linhas_antes}). "
        f"Tratamento célula por célula concluído."
    )

    return df[colunas_esperadas]
