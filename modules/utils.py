import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gastos")
        workbook = writer.book
        worksheet = writer.sheets["Gastos"]

        for i, col in enumerate(df.columns):
            col_series = df[col].astype(str)
            max_len = max(col_series.map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)

    return output.getvalue()

def aplicar_filtros(df, filtros_on, categorias_sel, data_ini, data_fim, vmin, vmax, texto):
    if not filtros_on or df.empty:
        return df

    df_filtrado = df.copy()

    if "Categoria" in df_filtrado.columns and categorias_sel:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias_sel)]

    if "Data" in df_filtrado.columns and not df_filtrado["Data"].isna().all():
        df_filtrado = df_filtrado[
            (df_filtrado["Data"] >= pd.to_datetime(data_ini)) &
            (df_filtrado["Data"] <= pd.to_datetime(data_fim))
        ]

    if "Valor" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado["Valor"] >= vmin) &
            (df_filtrado["Valor"] <= vmax)
        ]

    if texto.strip() and "Descrição" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado["Descrição"].str.contains(texto, case=False, na=False)
        ]

    return df_filtrado
