import pandas as pd
import numpy as np
import streamlit as st

def limpar_planilha(df, usar_ia=False, ia_resumo_fn=None, instrucoes_ia=""):
    # Cria uma cópia independente para segurança
    df_clean = df.copy()

    # ==========================================
    # 1. LIMPEZA ESTRUTURAL BÁSICA
    # ==========================================
    # Remove colunas e linhas que sejam 100% vazias (lixo de Excel)
    df_clean = df_clean.dropna(axis=1, how='all')
    df_clean = df_clean.dropna(axis=0, how='all')

    # Padroniza o nome das colunas removendo espaços ocultos nas pontas
    df_clean.columns = df_clean.columns.astype(str).str.strip().str.title()

    # ==========================================
    # 2. INFERÊNCIA INTELIGENTE DE TIPOS (Vetorizada)
    # ==========================================
    for col in df_clean.columns:
        # Pula colunas que já vieram perfeitamente tipadas como números
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            continue
            
        # Garante que a coluna é tratada como string para inspecionar a sujeira
        col_str = df_clean[col].astype(str)

        # --- A. DETECÇÃO DE MOEDA / NÚMEROS ---
        # Se achar 'R$', '$' no conteúdo, ou palavras-chave financeiras no título
        if col_str.str.contains(r'(?:R\$|\$)', regex=True, na=False).any() or \
           any(termo in col.upper() for termo in ["VALOR", "PREÇO", "PRECO", "TOTAL", "CUSTO", "SALDO"]):
            
            # Limpa tudo: tira R$, tira letras, tira ponto de milhar e arruma vírgula decimal
            limpo_num = col_str.str.replace(r'[a-zA-ZR\$\s]', '', regex=True) \
                               .str.replace('.', '', regex=False) \
                               .str.replace(',', '.', regex=False)
            
            convertido = pd.to_numeric(limpo_num, errors='coerce')
            
            # Se a conversão salvou pelo menos 30% dos dados da coluna, oficializa como numérica
            if convertido.notna().mean() > 0.3:
                df_clean[col] = convertido
                continue

        # --- B. DETECÇÃO DE DATAS ---
        if any(termo in col.upper() for termo in ["DATA", "VENCIMENTO", "EMISSÃO", "EMISSAO", "PERÍODO"]):
            convertido_data = pd.to_datetime(df_clean[col], errors='coerce', dayfirst=True)
            if convertido_data.notna().mean() > 0.3:
                df_clean[col] = convertido_data
                continue

        # --- C. LIMPEZA DE TEXTO (O que sobrou) ---
        if pd.api.types.is_string_dtype(df_clean[col]) or pd.api.types.is_object_dtype(df_clean[col]):
            # Remove espaços duplos, trailing spaces e normaliza 'nan' fantasma
            df_clean[col] = df_clean[col].apply(
                lambda x: str(x).strip() if pd.notna(x) and str(x).strip().lower() != 'nan' else np.nan
            )

    # ==========================================
    # 3. GATILHO DA IA (PocketDBA)
    # ==========================================
    if usar_ia and ia_resumo_fn is not None:
        # Apenas dispara a IA. O print visual é tratado lá no planilhas.py
        resumo = ia_resumo_fn(df_clean, instrucoes_ia=instrucoes_ia)
    else:
        st.success("🧹 Base de dados higienizada com sucesso pelo ETL Dinâmico.")

    return df_clean
