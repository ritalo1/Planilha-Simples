import pandas as pd

def criar_coluna(df, nome_coluna, valor_padrao=None):
    if nome_coluna and nome_coluna not in df.columns:
        df[nome_coluna] = valor_padrao
    return df

def substituir_valores(df, coluna, antigo, novo):
    if coluna in df.columns and antigo != "":
        df[coluna] = df[coluna].replace(antigo, novo)
    return df

def preencher_vazios(df, coluna, valor):
    if coluna in df.columns:
        df[coluna] = df[coluna].apply(lambda x: valor if (x is None or (isinstance(x, str) and x.strip() == "")) else x)
    return df

def regra_condicional_simples(df, col_ref, operador, limite, nome_saida, valor_true, valor_false=None):
    if col_ref not in df.columns or not nome_saida:
        return df

    def aplica_regra(x):
        try:
            if operador == ">":
                return valor_true if x > limite else valor_false
            if operador == ">=":
                return valor_true if x >= limite else valor_false
            if operador == "<":
                return valor_true if x < limite else valor_false
            if operador == "<=":
                return valor_true if x <= limite else valor_false
            if operador == "==":
                return valor_true if x == limite else valor_false
        except Exception:
            return valor_false
    df[nome_saida] = df[col_ref].apply(aplica_regra)
    return df
