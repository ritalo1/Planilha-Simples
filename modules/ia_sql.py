import streamlit as st
import google.generativeai as genai

API_KEY = st.secrets.get("GEMINI_API_KEY")
if API_KEY is None:
    raise RuntimeError("❌ GEMINI_API_KEY não foi carregado pelo Streamlit Cloud.")

genai.configure(api_key=API_KEY)

# MODELO CORRETO PARA STREAMLIT CLOUD (v1beta)
MODEL = genai.GenerativeModel("models/gemini-1.5-flash")

def corrigir_sql(query):
    prompt = f"""
Você é um DBA sênior especialista.
Corrija o SQL abaixo e retorne APENAS o código SQL corrigido.

SQL:
{query}
"""
    resposta = MODEL.generate_text(prompt)
    return resposta.text.strip()

def chat_dba(mensagem, historico):
    prompt = f"""
Você é um DBA sênior especialista.
Responda de forma clara e objetiva, sem termos técnicos.

Histórico:
{historico}

Usuário:
{mensagem}
"""
    resposta = MODEL.generate_text(prompt)
    return resposta.text.strip()

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

Não use termos técnicos. Não use SQL, mas resuma o que você entendeu. Caso não tenha entendido algo, foque e depure outros detalhes e explique brevemente sobre o que está ambíguo. Rode um relatório simples e fácil de entender, para o usuário conseguir corrigir a ambiguidade.

Planilha (amostra em CSV):
{amostra}
"""
    resposta = MODEL.generate_text(prompt)
    return resposta.text.strip()
