import pandas as pd

# ==========================================
# FUNCIÓN AUXILIAR: DETECCIÓN DE OUTLIERS
# ==========================================
def iqr_outliers(df: pd.DataFrame, column: str) -> list:
    """
    Detecta outliers usando el método de Rango Intercuartílico (IQR).
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame que contiene la columna a analizar
    column : str
        Nombre de la columna numérica a analizar
    
    Retorna:
    --------
    list : Índices de las filas que contienen outliers
    
    Método IQR:
    - Q1: Percentil 25
    - Q3: Percentil 75
    - IQR = Q3 - Q1
    - Límite inferior: Q1 - 1.5 * IQR
    - Límite superior: Q3 + 1.5 * IQR
    
    Ejemplo:
    --------
    outliers = iqr_outliers(df, 'Costo_Unitario_USD')
    # Retorna: [12, 45, 234] <- índices de filas con outliers
    """
    # Calcular Q1, Q3 e IQR
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Definir límites
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Retornar índices de valores fuera de rango
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index.tolist()
    return outliers

 
# ==========================================
# FUNCIÓN AUXILIAR: EXTRACCIÓN DE LEAD TIME
# ==========================================
def select_max_lead_time(string):
    """
    Extrae el valor máximo de un string de Lead_Time.
    
    Casos manejados:
    - "5" -> 5
    - "2-5" -> 5 (máximo del rango)
    - "inmediato" -> convertido a "1" antes -> 1
    - NaN -> retorna NaN
    
    Parámetros:
    -----------
    string : str o NaN
        String del lead time
    
    Retorna:
    --------
    int o NaN : Valor máximo o NaN si es nulo
    
    Ejemplo:
    --------
    select_max_lead_time("2-5 días") -> 5
    select_max_lead_time("inmediato") -> 1
    select_max_lead_time(NaN) -> NaN
    """
    if pd.isna(string):
        return pd.NA
    
    # Dividir por guión en caso de rango
    string_parts = string.strip().split('-')
    
    # Si es un solo valor
    if len(string_parts) == 1:
        return int(string_parts[0])
    # Si es un rango, retornar el máximo
    else:
        return max([int(part) for part in string_parts])


# ==========================================
# FUNCIÓN PRINCIPAL: PROCESAMIENTO INVENTARIO
# ==========================================
def procesar_inventario(inventario_path: str) -> pd.DataFrame:
    """
    Realiza limpieza, transformación e imputación de datos del inventario.
    
    Pasos de limpieza:
    1. Normalizar texto a minúsculas
    2. Limpiar Lead_Time_Dias
    3. Estandarizar categorías
    4. Convertir fechas a datetime
    5. Detectar outliers (IQR)
    6. Tratar valores extremos en costos
    7. Llenar nulos en stock
    8. Convertir valores negativos de stock a positivos
    
    Parámetros:
    -----------
    inventario_path : str
        Ruta del archivo CSV
    
    Retorna:
    --------
    pd.DataFrame : Inventario procesado y limpio
    """
    
    # Cargar CSV
    inventario = pd.read_csv(inventario_path)

    # ==========================================
    # PASO 1: NORMALIZACIÓN DE TEXTO
    # ==========================================
    # Extraer solo columnas de texto
    inventario_str = inventario.select_dtypes(include=['object'])
    
    # Convertir a minúsculas y eliminar espacios en blanco
    inventario_str = inventario_str.apply(lambda x: x.str.lower().str.strip())
    
    # ==========================================
    # PASO 2: LIMPIEZA DE LEAD_TIME_DIAS
    # ==========================================
    # Paso 2a: Eliminar unidad de medida " días"
    inventario_str.loc[:,'Lead_Time_Dias'] = inventario_str.loc[:,'Lead_Time_Dias'].str.replace(' días','', regex=False)
    
    # Paso 2b: Reemplazar "inmediato" por "1"
    inventario_str.loc[:,'Lead_Time_Dias'] = inventario_str.loc[:,'Lead_Time_Dias'].str.replace('inmediato','1', regex=False)

    # Paso 2c: Extraer máximo de rangos (e.g., "2-5" -> 5)
    inventario_str["Lead_Time_Dias"] = inventario_str["Lead_Time_Dias"].map(select_max_lead_time)
    
    # ==========================================
    # PASO 3: ESTANDARIZACIÓN DE CATEGORÍAS
    # ==========================================
    # Mapeo de variaciones a valores estándar
    dict_categorias = {
        "laptops": "laptop",              # Plural a singular
        "smart-phone": "smartphone",      # Formato con guión
        "smartphones": "smartphone",      # Plural a singular
        "???": ""                         # Valores nulos/desconocidos
    }
    
    # Aplicar mapeo, manteniendo valores no mapeados
    categoria_aux = inventario_str["Categoria"].map(dict_categorias).fillna(inventario_str["Categoria"])
    inventario_str["Categoria"] = categoria_aux

    # ==========================================
    # PASO 4: LIMPIEZA ADICIONAL DE TEXTO
    # ==========================================
    # Eliminar espacios en blanco de Bodega_Origen
    inventario_str['Bodega_Origen'] = inventario_str['Bodega_Origen'].str.strip()
    
    # Llenar nulos en Lead_Time_Dias con la mediana (5 días)
    inventario_str["Lead_Time_Dias"] = inventario_str["Lead_Time_Dias"].fillna(5)

    # ==========================================
    # PASO 5: CONVERSIÓN DE TIPOS DE DATO
    # ==========================================
    # Convertir fecha de string a datetime
    inventario_str["Ultima_Revision"] = pd.to_datetime(
        inventario_str["Ultima_Revision"], 
        format="%Y-%m-%d", 
        errors='coerce'
    )
    
    # Concatenar columnas de texto procesadas con columnas numéricas originales
    inventario_clean = pd.concat([inventario_str, inventario.select_dtypes('number')], axis=1)

    # ==========================================
    # PASO 6: DETECCIÓN DE OUTLIERS (IQR)
    # ==========================================
    # Detectar outliers en todas las columnas numéricas
    numeric_columns = inventario_clean.select_dtypes('number').columns
    outlier = {}
    for i in numeric_columns:
        outlier[i] = iqr_outliers(inventario_clean, column=i)
    # Nota: Los outliers se detectan pero el tratamiento es selectivo (ver paso 7)

    # ==========================================
    # PASO 7: TRATAMIENTO DE OUTLIERS ESPECÍFICOS
    # ==========================================
    # Calcular mediana de costos de smartphones válidos (excluyendo outliers obvios)
    usd_smartphones = inventario_clean.loc[
        lambda x: (x['Categoria'] == 'smartphone') & (x['Costo_Unitario_USD'] < 850000),
        'Costo_Unitario_USD'
    ].median()
    
    # Reemplazar valor erróneo en índice 500
    inventario_clean.loc[500, 'Costo_Unitario_USD'] = usd_smartphones
    
    # Reemplazar valores menores a 1 (claramente erróneos) con la mediana
    inventario_clean.loc[
        lambda x: x['Costo_Unitario_USD'] < 1, 
        'Costo_Unitario_USD'
    ] = usd_smartphones

    # ==========================================
    # PASO 8: IMPUTACIÓN DE STOCK_ACTUAL
    # ==========================================
    # Llenar valores nulos con 0 (sin stock disponible)
    inventario_clean['Stock_Actual'] = inventario_clean['Stock_Actual'].fillna(0)

    # Convertir valores negativos a positivos (datos erróneos de entrada)
    inventario_clean.loc[
        lambda x: x['Stock_Actual'] < 0, 
        'Stock_Actual'
    ] = -1 * inventario_clean.loc[
        lambda x: x['Stock_Actual'] < 0, 
        'Stock_Actual'
    ]

    return inventario_clean
