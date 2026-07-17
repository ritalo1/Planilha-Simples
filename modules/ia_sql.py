import streamlit as st
import google.generativeai as genai

API_KEY = st.secrets.get("GEMINI_API_KEY")
if API_KEY is None:
    raise RuntimeError("❌ GEMINI_API_KEY não foi carregado pelo Streamlit Cloud.")

genai.configure(api_key=API_KEY)

MODEL = genai.GenerativeModel("gemini-1.5-flash")

def corrigir_sql(query):
    prompt = f"""
Você é um DBA sênior especialista.
Seu papel é analisar o input SQL do usuário, corrigir erros de sintaxe comuns
e retornar APENAS o código SQL corrigido, sem explicações.

Você NÃO pode gerar código Python, nem editar arquivos do app.
Apenas SQL.

SQL do usuário:
{query}
"""
    resposta = MODEL.generate_content(prompt)
    return resposta.text.strip()

def chat_dba(mensagem, historico):
    prompt = f"""
Você é um DBA sênior especialista.
Responda de forma clara e objetiva, focando em dados, SQL e boas práticas.
Você NÃO pode editar o código do app, apenas orientar o usuário.

Histórico:
{historico}

Usuário:
{mensagem}
"""
    resposta = MODEL.generate_content(prompt)
    return resposta.text.strip()

def resumo_planilha(df):
    # usa CSV em vez de markdown, pra não depender de tabulate
    amostra = df.head(50).to_csv(index=False)

    prompt = f"""
Você é um DBA sênior explicando dados para um usuário leigo.
Explique de forma simples e breve o que essa planilha mostra:
- padrões
- valores altos
- categorias frequentes
- possíveis inconsistências
- qualquer insight útil

Não use termos técnicos. Não use SQL, mas explique e resuma o que entendeu. Se não entender algo, foque e detalhe outros pontos.

Planilha (amostra em CSV):
{amostra}
"""
    resposta = MODEL.generate_content(prompt)
    return resposta.text.strip()
