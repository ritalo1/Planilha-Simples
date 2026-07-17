import google.genai as genai
from google.genai import errors
import pandas as pd
import streamlit as st

API_KEY = st.secrets.get("GEMINI_API_KEY")
if API_KEY is None:
    raise RuntimeError("❌ GEMINI_API_KEY não foi carregado pelo Streamlit Cloud.")

client = genai.Client(api_key=API_KEY)

# Mantendo o flash para velocidade máxima no mobile
MODEL_NAME = "models/gemini-3.5-flash"


def corrigir_sql(query):
    prompt = f"""
Você é um DBA sênior especialista.
Corrija o SQL abaixo e retorne APENAS o código SQL corrigido.

SQL:
{query}
"""
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "max_output_tokens": 300,
                "temperature": 0.1  # Ultra focado e direto
            }
        )
        return resp.text.strip()
    except errors.ServerError:
        return "-- ⚠️ Servidor Gemini instável. Tente enviar a query novamente."
    except Exception as e:
        return f"-- ⚠️ Erro ao corrigir SQL: {str(e)}"


def chat_dba(mensagem, historico):
    prompt = f"""
Você é um DBA sênior especialista.
Responda de forma clara e objetiva, focando em usabilidade prática.

Histórico:
{historico}

Usuário:
{mensagem}
"""
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "max_output_tokens": 400,
                "temperature": 0.3
            }
        )
        return resp.text.strip()
    except errors.ServerError:
        return "⚠️ O servidor do PocketDBA oscilou. Pode repetir a última pergunta?"
    except Exception as e:
        return f"⚠️ Erro no chat: {str(e)}"


def resumo_planilha(df, instrucoes_ia=""):
    # Reduzido para 35 linhas para acelerar o tráfego de dados e manter precisão
    amostra = df.head(35).fillna("").to_csv(index=False)

    contexto_usuario = ""
    if instrucoes_ia:
        contexto_usuario = f"""
O usuário enviou regras e focos específicos para esta análise:
REGRAS DO USUÁRIO: "{instrucoes_ia}"
Leve as regras acima em consideração máxima ao gerar o relatório.
"""

    prompt = f"""
Você é um DBA sênior explicando dados para um analista.
Explique o que essa planilha mostra.

{contexto_usuario}

Foque em resumir:
- padrões encontrados
- valores altos ou discrepantes
- categorias mais frequentes
- possíveis inconsistências ou sujeiras nos dados
- qualquer insight útil para tomada de decisão

Não use termos técnicos complexos ou códigos SQL brutos.

Planilha (amostra em CSV):
{amostra}

Restrições de Resposta:
- Mantenha uma introdução e encerramento curtos e amigáveis.
- O miolo do relatório DEVE ser extremamente conciso, direto e estruturado em tópicos (bullet points) usando Markdown.
- Evite parágrafos longos para acelerar o tempo de geração.
"""
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "max_output_tokens": 450, # Espaço ideal para introdução + tópicos + fechamento
                "temperature": 0.2        # Resposta mais rápida e assertiva
            }
        )
        
        # Envelopa o retorno simulando a caixinha de identidade do PocketDBA
        resposta_formatada = f"""
### <span style='color:#9b5de5;'>[📊] Pocket</span><span style='color:#fbc490;'>DBA</span>
---
{resp.text.strip()}
"""
        return resposta_formatada

    except errors.ServerError:
        return (
            "⚠️ O servidor do Gemini encontrou uma instabilidade temporária ao processar a planilha. "
            "Por favor, tente clicar em Enviar novamente."
        )
    except errors.APIError as e:
        return f"⚠️ Falha de comunicação com a API do PocketDBA: {e.message}"
    except Exception as e:
        return f"⚠️ Erro inesperado no motor de IA: {str(e)}"
