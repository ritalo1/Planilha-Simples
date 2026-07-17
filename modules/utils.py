from io import BytesIO
import pandas as pd


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gastos")
        workbook = writer.book
        worksheet = writer.sheets["Gastos"]

        for i, col in enumerate(df.columns):
            # Substitui valores nulos por texto vazio antes de converter para string
            # Isso evita que nulos virem a palavra "nan" e mexam na largura
            col_series = df[col].fillna("").astype(str)

            # Agora o map(len) roda seguro porque tudo é string de verdade
            max_len = max(col_series.map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)

    # Reseta o ponteiro do arquivo para o início (essencial para o Streamlit)
    output.seek(0)
    return output.getvalue()
