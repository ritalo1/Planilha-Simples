import streamlit as st
import pandas as pd
from modules.etl import limpar_planilha
from modules.utils import to_excel
from modules.transformacoes import (
    criar_coluna, substituir_valores, preencher_vazios, regra_condicional_simples
)
from modules.ia_sql import resumo_planilha

def render_planilhas(df, nome):
    st.markdown(
        f"<h3 style='color:#9b5de5;'>[🧾] Planilhas — {nome}</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#BBBBBB; font-size:14px;'>Edite, limpe e transforme seus dados com ferramentas rápidas.</p>",
        unsafe_allow_html=True
    )

    # Importar
    st.subheader("[📥] Importar planilha")
    arquivo = st.file_uploader(
        "Selecione um arquivo",
        type=["xlsx", "xlsm", "ods", "csv", "tsv"],
        key=f"upload_{nome}"
    )

    if arquivo:
        nome_arquivo = arquivo.name.lower()

        if nome_arquivo.endswith((".csv", ".tsv")):
            df_importado = pd.read_csv(arquivo)
        else:
            df_importado = pd.read_excel(arquivo)

        df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()].copy()
        colunas_detectadas = list(df_importado.columns)

        st.info("Mapeie as colunas do arquivo para o padrão do PocketDBA:")

        col_desc = st.selectbox("Coluna de Descrição", colunas_detectadas, key=f"map_desc_{nome}")
        col_cat = st.selectbox("Coluna de Categoria", colunas_detectadas, key=f"map_cat_{nome}")
        col_val = st.selectbox("Coluna de Valor", colunas_detectadas, key=f"map_val_{nome}")
        col_data = st.selectbox("Coluna de Data", colunas_detectadas, key=f"map_data_{nome}")

        if st.button("Confirmar mapeamento e limpar", key=f"map_btn_{nome}"):

            df_importado = df_importado.rename(columns={
                col_desc: "Descrição",
                col_cat: "Categoria",
                col_val: "Valor",
                col_data: "Data"
            })

            df_importado = df_importado.loc[:, ~df_importado.columns.duplicated()].copy()
            df_importado = limpar_planilha(df_importado)

            st.session_state.planilhas[nome] = df_importado
            df = df_importado

            st.success("Planilha importada, mapeada e limpa com sucesso!")

    # Estado
    if "planilhas" not in st.session_state:
        st.session_state.planilhas = {}
    if nome not in st.session_state.planilhas:
        st.session_state.planilhas[nome] = df

    # Editor
    st.subheader("[✏️] Editar dados")
    df = st.session_state.planilhas[nome]
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df = df.reset_index(drop=True)

    st.session_state.planilhas[nome] = st.data_editor(
        df,
        num_rows="dynamic",
        key=f"editor_{nome}",
        use_container_width=True
    )

    # Ferramentas simples
    st.markdown("### [🛠] Ferramentas rápidas")

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)

    with col_t1:
        st.markdown("**➕ Criar coluna**")
        nome_col = st.text_input("Nome da nova coluna", key=f"nova_col_{nome}")
        valor_padrao = st.text_input("Valor padrão (opcional)", key=f"nova_col_val_{nome}")
        if st.button("Criar", key=f"btn_criar_col_{nome}"):
            df = st.session_state.planilhas[nome]
            df = criar_coluna(df, nome_col, valor_padrao or None)
            st.session_state.planilhas[nome] = df
            st.success(f"Coluna '{nome_col}' criada.")

    with col_t2:
        st.markdown("**🔁 Substituir valores**")
        col_sub = st.selectbox("Coluna", df.columns, key=f"sub_col_{nome}")
        antigo = st.text_input("Valor antigo", key=f"sub_ant_{nome}")
        novo = st.text_input("Valor novo", key=f"sub_novo_{nome}")
        if st.button("Substituir", key=f"btn_sub_{nome}"):
            df = st.session_state.planilhas[nome]
            df = substituir_valores(df, col_sub, antigo, novo)
            st.session_state.planilhas[nome] = df
            st.success("Substituição aplicada.")

    with col_t3:
        st.markdown("**🧩 Preencher vazios**")
        col_vaz = st.selectbox("Coluna", df.columns, key=f"vaz_col_{nome}")
        val_vaz = st.text_input("Valor para vazios", key=f"vaz_val_{nome}")
        if st.button("Preencher", key=f"btn_vaz_{nome}"):
            df = st.session_state.planilhas[nome]
            df = preencher_vazios(df, col_vaz, val_vaz)
            st.session_state.planilhas[nome] = df
            st.success("Vazios preenchidos.")

    with col_t4:
        st.markdown("**⚖ Regra simples**")
        col_ref = st.selectbox("Coluna de referência", df.columns, key=f"reg_col_{nome}")
        operador = st.selectbox("Operador", [">", ">=", "<", "<=", "=="], key=f"reg_op_{nome}")
        limite = st.number_input("Limite", key=f"reg_lim_{nome}")
        nome_saida = st.text_input("Nome da coluna de saída", key=f"reg_out_{nome}")
        val_true = st.text_input("Valor se verdadeiro", key=f"reg_true_{nome}")
        val_false = st.text_input("Valor se falso (opcional)", key=f"reg_false_{nome}")
        if st.button("Aplicar regra", key=f"btn_reg_{nome}"):
            df = st.session_state.planilhas[nome]
            df = regra_condicional_simples(df, col_ref, operador, limite, nome_saida, val_true, val_false or None)
            st.session_state.planilhas[nome] = df
            st.success("Regra aplicada.")

    # Caixa de IA abaixo da planilha
    st.markdown("### [🤖] Assistente IA para a planilha")
    msg = st.text_area("Peça algo sobre esta planilha (ex.: 'Me dê um resumo.')", key=f"ia_msg_{nome}")
    if st.button("Me dê um resumo.", key=f"btn_resumo_{nome}"):
        df_atual = st.session_state.planilhas[nome]
        resumo = resumo_planilha(df_atual)
        if "ia_log" not in st.session_state:
            st.session_state.ia_log = ""
        st.session_state.ia_log += f"\n\n[Resumo PocketDBA]\n{resumo}"
        st.success("Resumo gerado. Veja na janela de IA no canto da tela.")
        st.write(resumo)

    # Ações
    st.markdown("### [📦] Ações")

    col_b1, col_b2, col_b3 = st.columns(3)

    with col_b1:
        if st.button(f"🧹 Limpar planilha — {nome}"):
            df_limpo = limpar_planilha(st.session_state.planilhas[nome])
            st.session_state.planilhas[nome] = df_limpo
            st.success("Planilha limpa.")

    with col_b2:
        if st.button(f"🧮 Calcular total — {nome}"):
            df_calc = limpar_planilha(st.session_state.planilhas[nome].copy())
            total = df_calc["Valor"].sum()
            st.success(f"Total de valores em {nome}: {total:,.2f}")

    with col_b3:
        df_export = st.session_state.planilhas[nome]
        st.download_button(
            label="[📤] Exportar para Excel",
            data=to_excel(df_export),
            file_name=f"{nome}.xlsx"
    )
