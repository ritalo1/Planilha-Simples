import google.generativeai as genai
import os

API_KEY = st.secrets.get("GEMINI_API_KEY")
  if API_KEY is None:
    raise RuntimeError("❌ GEMINI_API_KEY não foi carregado pelo Streamlit Cloud.")
genai.configure(api_key=API_KEY)

def corrigir_sql(query):
    prompt = f"""
Você é um DBA sênior especialista.
Seu papel é analisar o input SQL do usuário, corrigir erros de sintaxe comuns
e retornar APENAS o código SQL corrigido, sem explicações.
SQL do usuário:
{query}
"""

    resposta = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    return resposta.text.strip()

def chat_dba(mensagem, historico):
    prompt = f"""
Você é um DBA sênior especialista.
Responda de forma clara e objetiva. A resposta deve estar factualmente correta.
Histórico:
{historico}

Usuário:
{mensagem}
"""

    resposta = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    return resposta.text.strip()
