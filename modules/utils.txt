import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gastos")
    return output.getvalue()

def aplicar_filtros(df, filtros_on, categorias_sel, data_ini, data_fim, vmin, vmax, texto):
    if not filtros_on or df.empty:
        return df

    df_filtrado = df.copy()

    if categorias_sel:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias_sel)]

    if not df_filtrado["Data"].isna().all():
        df_filtrado = df_filtrado[
            (df_filtrado["Data"] >= pd.to_datetime(data_ini)) &
            (df_filtrado["Data"] <= pd.to_datetime(data_fim))
        ]

    df_filtrado = df_filtrado[
        (df_filtrado["Valor"] >= vmin) &
        (df_filtrado["Valor"] <= vmax)
    ]

    if texto.strip():
        df_filtrado = df_filtrado[
            df_filtrado["Descrição"].str.contains(texto, case=False, na=False)
        ]

    return df_filtrado
