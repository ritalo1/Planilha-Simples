import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gastos")
        workbook = writer.book
        worksheet = writer.sheets["Gastos"]

        for i, col in enumerate(df.columns):
            # converte tudo para string antes de medir tamanho
            col_series = df[col].astype(str)
            max_len = max(col_series.map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)

    return output.getvalue()
