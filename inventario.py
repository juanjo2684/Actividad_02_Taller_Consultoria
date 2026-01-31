import pandas as pd

def iqr_outliers(df: pd.DataFrame, column: str) -> list:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index.tolist()
    return outliers
 
def select_max_lead_time(string):
    if pd.isna(string):
        return pd.NA
    string_parts = string.strip().split('-')
    if len(string_parts) == 1:
        return int(string_parts[0])
    else:
        return max([int(part) for part in string_parts])

def procesar_inventario(inventario_path: str) -> pd.DataFrame:
    
    inventario = pd.read_csv(inventario_path)

    inventario_str = inventario.select_dtypes(include=['object'])
    inventario_str = inventario_str.apply(lambda x: x.str.lower().str.strip())
    inventario_str.loc[:,'Lead_Time_Dias'] = inventario_str.loc[:,'Lead_Time_Dias'].str.replace(' días','', regex=False)
    inventario_str.loc[:,'Lead_Time_Dias'] = inventario_str.loc[:,'Lead_Time_Dias'].str.replace('inmediato','1', regex=False)

    inventario_str["Lead_Time_Dias"] = inventario_str["Lead_Time_Dias"].map(select_max_lead_time)
    dict_categorias = {"laptops":"laptop",
                       "smart-phone":"smartphone",
                       "smartphones":"smartphone",
                       "???":""}
    
    categoria_aux = inventario_str["Categoria"].map(dict_categorias).fillna(inventario_str["Categoria"])
    inventario_str["Categoria"] = categoria_aux

    inventario_str['Bodega_Origen'] = inventario_str['Bodega_Origen'].str.strip()
    inventario_str["Lead_Time_Dias"] = inventario_str["Lead_Time_Dias"].fillna(5)

    inventario_str["Ultima_Revision"] = pd.to_datetime(inventario_str["Ultima_Revision"], format="%Y-%m-%d", errors='coerce')
    
    inventario_clean =pd.concat([inventario_str, inventario.select_dtypes('number')], axis=1)

    numeric_columns = inventario_clean.select_dtypes('number').columns
    outlier = {}
    for i in numeric_columns:
        outlier[i] = iqr_outliers(inventario_clean, column=i)

    usd_smartphones =inventario_clean.loc[lambda x:(x['Categoria']=='smartphone') & (x['Costo_Unitario_USD']< 850000),'Costo_Unitario_USD'].median()
    inventario_clean.loc[500, 'Costo_Unitario_USD'] = usd_smartphones
    inventario_clean.loc[lambda x: x['Costo_Unitario_USD'] < 1, 'Costo_Unitario_USD'] = usd_smartphones

    inventario_clean['Stock_Actual'] = inventario_clean['Stock_Actual'].fillna(0)

    inventario_clean.loc[lambda x: x['Stock_Actual'] < 0, 'Stock_Actual'] = -1*inventario_clean.loc[lambda x: x['Stock_Actual'] < 0, 'Stock_Actual']

    return inventario_clean