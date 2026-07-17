import streamlit as st
import google.genai as genai

API_KEY = st.secrets.get("GEMINI_API_KEY")
if API_KEY is None:
    raise RuntimeError("❌ GEMINI_API_KEY não foi carregado pelo Streamlit Cloud.")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "models/gemini-3.5-flash"

def corrigir_sql(query):
    prompt = f"""
Você é um DBA sênior especialista.
Corrija o SQL abaixo e retorne APENAS o código SQL corrigido.

SQL:
{query}
"""
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return resp.text.strip()

def chat_dba(mensagem, historico):
    prompt = f"""
Você é um DBA sênior especialista.
Responda de forma clara e objetiva, sem termos técnicos.

Histórico:
{historico}

Usuário:
{mensagem}
"""
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return resp.text.strip()

def resumo_planilha(df):
    amostra = df.head(50).to_csv(index=False)
    prompt = f"""
Você é um DBA sênior explicando dados para um usuário leigo.
Explique de forma simples e breve o que essa planilha mostra:
- padrões
- valores altos
- categorias frequentes
- possíveis inconsistências
- qualquer insight útil

Não use termos técnicos. Não use SQL.

Planilha (amostra em CSV):
{amostra}
"""
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return resp.text.strip()
