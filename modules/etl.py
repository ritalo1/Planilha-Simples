import pandas as pd
import streamlit as st

CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia",
    "Saúde", "Lazer", "Educação", "Outros"
]

def limpar_planilha(df, usar_ia=False, ia_resumo_fn=None, instrucoes_ia=""):
    if usar_ia and instrucoes_ia:
        # Você junta o prompt padrão do seu ETL com o pedido do usuário:
        prompt_completo = f"Instruções extras do usuário para aplicar no arquivo: {instrucoes_ia}"
        # ... envia o prompt_completo para a IA ...

def limpar_planilha(df, usar_ia=False, ia_resumo_fn=None):
    df = df.copy()

    # Padroniza nomes das colunas
    df.columns = df.columns.str.strip().str.title()

    # Garante colunas esperadas
    colunas_esperadas = ["Descrição", "Categoria", "Data", "Valor", "Observações"]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = None

    # Tratamento célula por célula (sem 0.1)
    for linha in df.index:
        for coluna in df.columns:
            valor = df.at[linha, coluna]

            if coluna == "Descrição":
                df.at[linha, coluna] = "" if valor is None else str(valor).strip()

            elif coluna == "Categoria":
                texto = str(valor).strip() if valor else "Outros"
                df.at[linha, coluna] = texto if texto in CATEGORIAS else "Outros"

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

            elif coluna == "Valor":
                if isinstance(valor, (int, float)):
                    continue
                if isinstance(valor, str) and valor.strip():
                    raw = valor.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                    try:
                        df.at[linha, coluna] = float(raw)
                    except:
                        df.at[linha, coluna] = None
                else:
                    df.at[linha, coluna] = None

            elif coluna == "Observações":
                df.at[linha, coluna] = "" if valor is None else str(valor).strip()

    # Organiza por categoria
    df = df.sort_values(by="Categoria")

    if usar_ia and ia_resumo_fn is not None:
        resumo = ia_resumo_fn(df)
        st.info(f"[🤖] PocketDBA auxiliou na limpeza:\n\n{resumo}")
    else:
        st.success("🧹 Planilha limpa e organizada por categoria.")

    return df[colunas_esperadas]
