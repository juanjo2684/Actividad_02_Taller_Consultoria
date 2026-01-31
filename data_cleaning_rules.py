# ==========================================
# DATA CLEANING RULES DOCUMENTATION
# ==========================================
# Este módulo contiene la documentación de todas las reglas de limpieza
# aplicadas a cada dataset, facilitando su visualización en Streamlit

# ==========================================
# 1. REGLAS DE LIMPIEZA - INVENTARIO
# ==========================================
INVENTARIO_CLEANING_RULES = {
    "dataset": "Inventario",
    "rules": [
        {
            "nombre": "Normalización de texto",
            "descripcion": "Convertir todas las columnas de texto a minúsculas y eliminar espacios en blanco",
            "variables_afectadas": ["Lead_Time_Dias", "Categoria", "Bodega_Origen"],
            "tipo": "Normalización",
            "codigo": "inventario_str.apply(lambda x: x.str.lower().str.strip())",
            "impacto": "Estandarización de datos de texto"
        },
        {
            "nombre": "Limpieza Lead_Time_Dias",
            "descripcion": "Eliminar unidad ' días', reemplazar 'inmediato' por '1', y extraer valor máximo de rangos",
            "variables_afectadas": ["Lead_Time_Dias"],
            "tipo": "Transformación",
            "codigo": """
# Paso 1: Eliminar ' días'
inventario_str.loc[:,'Lead_Time_Dias'] = inventario_str.loc[:,'Lead_Time_Dias'].str.replace(' días','', regex=False)

# Paso 2: Reemplazar 'inmediato' por '1'
inventario_str.loc[:,'Lead_Time_Dias'] = inventario_str.loc[:,'Lead_Time_Dias'].str.replace('inmediato','1', regex=False)

# Paso 3: Aplicar función para extraer máximo de rangos (ej: '2-5' -> 5)
inventario_str["Lead_Time_Dias"] = inventario_str["Lead_Time_Dias"].map(select_max_lead_time)
            """,
            "impacto": "Conversión de texto a valores numéricos"
        },
        {
            "nombre": "Estandarización Categoria",
            "descripcion": "Mapear variaciones de nombres de categorías a valores estándar",
            "variables_afectadas": ["Categoria"],
            "tipo": "Mapeo de valores",
            "codigo": """
dict_categorias = {
    "laptops": "laptop",
    "smart-phone": "smartphone",
    "smartphones": "smartphone",
    "???": ""
}
categoria_aux = inventario_str["Categoria"].map(dict_categorias).fillna(inventario_str["Categoria"])
inventario_str["Categoria"] = categoria_aux
            """,
            "impacto": "Eliminación de duplicados categoriales (ej: 'laptops' -> 'laptop')"
        },
        {
            "nombre": "Imputación Lead_Time_Dias",
            "descripcion": "Llenar valores nulos con la mediana (5)",
            "variables_afectadas": ["Lead_Time_Dias"],
            "tipo": "Imputación",
            "codigo": "inventario_str[\"Lead_Time_Dias\"] = inventario_str[\"Lead_Time_Dias\"].fillna(5)",
            "impacto": "Eliminación de valores nulos"
        },
        {
            "nombre": "Conversión de fecha",
            "descripcion": "Convertir formato de fecha a datetime",
            "variables_afectadas": ["Ultima_Revision"],
            "tipo": "Transformación de tipo",
            "codigo": "inventario_str[\"Ultima_Revision\"] = pd.to_datetime(inventario_str[\"Ultima_Revision\"], format=\"%Y-%m-%d\", errors='coerce')",
            "impacto": "Conversión correcta de tipos de datos"
        },
        {
            "nombre": "Detección de outliers",
            "descripcion": "Identificar outliers usando método IQR (1.5 * IQR)",
            "variables_afectadas": ["Todas las numéricas"],
            "tipo": "Detección",
            "codigo": """
# Función IQR
Q1 = df[column].quantile(0.25)
Q3 = df[column].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
            """,
            "impacto": "Identificación de valores extremos para revisión"
        },
        {
            "nombre": "Tratamiento Costo_Unitario_USD",
            "descripcion": "Reemplazar outliers y valores menores a 1 con la mediana de smartphones",
            "variables_afectadas": ["Costo_Unitario_USD"],
            "tipo": "Tratamiento de outliers",
            "codigo": """
# Calcular mediana de smartphones válidos
usd_smartphones = inventario_clean.loc[
    (inventario_clean['Categoria']=='smartphone') & (inventario_clean['Costo_Unitario_USD']< 850000),
    'Costo_Unitario_USD'
].median()

# Reemplazar valor en índice 500
inventario_clean.loc[500, 'Costo_Unitario_USD'] = usd_smartphones

# Reemplazar valores menores a 1
inventario_clean.loc[lambda x: x['Costo_Unitario_USD'] < 1, 'Costo_Unitario_USD'] = usd_smartphones
            """,
            "impacto": "Corrección de valores erróneos y outliers"
        },
        {
            "nombre": "Imputación Stock_Actual",
            "descripcion": "Llenar valores nulos con 0",
            "variables_afectadas": ["Stock_Actual"],
            "tipo": "Imputación",
            "codigo": "inventario_clean['Stock_Actual'] = inventario_clean['Stock_Actual'].fillna(0)",
            "impacto": "Eliminación de valores nulos"
        },
        {
            "nombre": "Conversión Stock_Actual negativo",
            "descripcion": "Convertir valores negativos a positivos",
            "variables_afectadas": ["Stock_Actual"],
            "tipo": "Transformación",
            "codigo": "inventario_clean.loc[lambda x: x['Stock_Actual'] < 0, 'Stock_Actual'] = -1*inventario_clean.loc[lambda x: x['Stock_Actual'] < 0, 'Stock_Actual']",
            "impacto": "Garantía de valores positivos para cantidades de stock"
        }
    ]
}

# ==========================================
# 2. REGLAS DE LIMPIEZA - FEEDBACK
# ==========================================
FEEDBACK_CLEANING_RULES = {
    "dataset": "Feedback",
    "rules": [
        {
            "nombre": "Eliminación de duplicados",
            "descripcion": "Remover filas completamente duplicadas",
            "variables_afectadas": ["Todas"],
            "tipo": "Deduplicación",
            "codigo": "df = df.drop_duplicates()",
            "impacto": "Eliminación de registros redundantes"
        },
        {
            "nombre": "Imputación Edad_Cliente",
            "descripcion": "Reemplazar edades fuera del rango [18, 90] con la mediana de edades válidas",
            "variables_afectadas": ["Edad_Cliente"],
            "tipo": "Imputación",
            "codigo": """
edad_mediana = df.loc[df["Edad_Cliente"].between(18, 90), "Edad_Cliente"].median()
df.loc[~df["Edad_Cliente"].between(18, 90), "Edad_Cliente"] = edad_mediana
            """,
            "impacto": "Reemplazo de valores ilógicos por mediana válida"
        },
        {
            "nombre": "Normalización Recomienda_Marca",
            "descripcion": "Convertir a mayúsculas, normalizar 'SÍ' a 'SI', mapear '0' a 'NO'",
            "variables_afectadas": ["Recomienda_Marca"],
            "tipo": "Normalización",
            "codigo": """
df["Recomienda_Marca"] = (
    df["Recomienda_Marca"]
    .astype("string")
    .str.strip()
    .str.upper()
    .replace({"0": "NO", "SÍ": "SI"})
)
            """,
            "impacto": "Estandarización y normalización de valores binarios"
        },
        {
            "nombre": "Imputación Recomienda_Marca",
            "descripcion": "Llenar valores nulos con la moda",
            "variables_afectadas": ["Recomienda_Marca"],
            "tipo": "Imputación",
            "codigo": """
moda_recomienda = df["Recomienda_Marca"].mode()[0]
df["Recomienda_Marca"] = df["Recomienda_Marca"].fillna(moda_recomienda)
            """,
            "impacto": "Eliminación de valores nulos con valor más frecuente"
        },
        {
            "nombre": "Normalización Ticket_Soporte_Abierto",
            "descripcion": "Convertir a mayúsculas, normalizar variantes y mapear a booleano",
            "variables_afectadas": ["Ticket_Soporte_Abierto"],
            "tipo": "Normalización",
            "codigo": """
df["Ticket_Soporte_Abierto"] = (
    df["Ticket_Soporte_Abierto"]
    .astype("string")
    .str.strip()
    .str.upper()
    .replace({"SÍ": "SI", "0": "NO"})
)
df["Ticket_Soporte_Abierto"] = df["Ticket_Soporte_Abierto"].map({"SI": True, "NO": False})
            """,
            "impacto": "Conversión a tipo booleano con normalización"
        },
        {
            "nombre": "Conversión de texto",
            "descripcion": "Asegurar que comentarios sean string",
            "variables_afectadas": ["Comentario_Texto"],
            "tipo": "Conversión de tipo",
            "codigo": "df[\"Comentario_Texto\"] = df[\"Comentario_Texto\"].astype(\"string\")",
            "impacto": "Garantía de tipo de dato correcto"
        }
    ]
}

# ==========================================
# 3. REGLAS DE LIMPIEZA - TRANSACCIONES
# ==========================================
TRANSACCIONES_CLEANING_RULES = {
    "dataset": "Transacciones",
    "rules": [
        {
            "nombre": "Conversión de fecha",
            "descripcion": "Convertir Fecha_Venta a datetime",
            "variables_afectadas": ["Fecha_Venta"],
            "tipo": "Conversión de tipo",
            "codigo": "df_transacciones['Fecha_Venta'] = pd.to_datetime(df_transacciones['Fecha_Venta'])",
            "impacto": "Formato correcto para análisis temporal"
        },
        {
            "nombre": "Normalización de texto",
            "descripcion": "Convertir todas las columnas de texto a minúsculas",
            "variables_afectadas": ["Todas las columnas object/string"],
            "tipo": "Normalización",
            "codigo": """
cols_texto = df_transacciones.select_dtypes(include=['object', 'string']).columns
df_transacciones[cols_texto] = df_transacciones[cols_texto].apply(lambda x: x.str.lower())
            """,
            "impacto": "Estandarización de texto para comparaciones"
        },
        {
            "nombre": "Conversión Cantidad_Vendida a positivo",
            "descripcion": "Convertir valores negativos en cantidad vendida a positivos",
            "variables_afectadas": ["Cantidad_Vendida"],
            "tipo": "Transformación",
            "codigo": "df_transacciones.loc[:,'Cantidad_Vendida'] = df_transacciones.loc[:,'Cantidad_Vendida'].abs()",
            "impacto": "Garantía de valores positivos para cantidades"
        },
        {
            "nombre": "Imputación Estado_Envio (sin ticket)",
            "descripcion": "Llenar Estados_Envio vacíos con 'entregado' para transacciones sin ticket de soporte",
            "variables_afectadas": ["Estado_Envio"],
            "tipo": "Imputación condicional",
            "codigo": """
transacciones_nps_no = df_feedback['Transaccion_ID'].unique()
condicion_existe = df_transacciones['Transaccion_ID'].isin(transacciones_nps_no)
condicion_vacio = df_transacciones['Estado_Envio'].isna()
df_transacciones.loc[condicion_existe & condicion_vacio, 'Estado_Envio'] = 'entregado'
            """,
            "impacto": "Imputación lógica basada en datos relacionales"
        },
        {
            "nombre": "Imputación Estado_Envio (con ticket)",
            "descripcion": "Llenar Estados_Envio vacíos con 'devuelto' para transacciones con ticket abierto",
            "variables_afectadas": ["Estado_Envio"],
            "tipo": "Imputación condicional",
            "codigo": """
transacciones_nps_si = df_feedback['Transaccion_ID'].unique()
condicion_existe = df_transacciones['Transaccion_ID'].isin(transacciones_nps_si)
condicion_vacio = df_transacciones['Estado_Envio'].isna()
df_transacciones.loc[condicion_existe & condicion_vacio, 'Estado_Envio'] = 'devuelto'
            """,
            "impacto": "Inferencia de estado basada en problema de soporte"
        },
        {
            "nombre": "Normalización de ciudades",
            "descripcion": "Mapear abreviaturas a nombres completos",
            "variables_afectadas": ["Ciudad_Destino"],
            "tipo": "Mapeo de valores",
            "codigo": """
dic_ciudades = {'bog': 'bogotá', 'med': 'medellín'}
df_transacciones.replace(dic_ciudades, inplace=True)
            """,
            "impacto": "Estandarización de nombres de ciudades"
        },
        {
            "nombre": "Imputación Costo_Envio (canal físico)",
            "descripcion": "Llenar Costo_Envio con 0 para ventas en canal físico",
            "variables_afectadas": ["Costo_Envio"],
            "tipo": "Imputación condicional",
            "codigo": "df_transacciones.loc[df_transacciones['Canal_Venta'] == 'físico', 'Costo_Envio'] = 0",
            "impacto": "Lógica comercial: sin envío en tienda física"
        },
        {
            "nombre": "Creación de variable Margen",
            "descripcion": "Calcular margen absoluto y porcentual",
            "variables_afectadas": ["margen", "margen %"],
            "tipo": "Feature engineering",
            "codigo": """
df_transacciones['margen'] = df_transacciones['Precio_Venta_Final'] - df_transacciones['Costo_Envio']
df_transacciones['margen %'] = df_transacciones['margen'] / df_transacciones['Precio_Venta_Final']
            """,
            "impacto": "Creación de métricas de rentabilidad"
        },
        {
            "nombre": "Merge con inventario",
            "descripcion": "Traer Bodega_Origen del inventario usando SKU_ID",
            "variables_afectadas": ["Bodega_Origen (nueva)"],
            "tipo": "Enriquecimiento de datos",
            "codigo": """
df_transacciones = df_transacciones.merge(
    df_inventario[['SKU_ID', 'Bodega_Origen']],
    on='SKU_ID',
    how='left'
)
            """,
            "impacto": "Vinculación con información de inventario"
        },
        {
            "nombre": "Creación ID de tiempos de entrega",
            "descripcion": "Crear identificador para imputación grupal",
            "variables_afectadas": ["id_tiempos_entrega (nueva)"],
            "tipo": "Transformación",
            "codigo": "df_transacciones['id_tiempos_entrega'] = df_transacciones['Bodega_Origen'] + '-' + df_transacciones['Ciudad_Destino']",
            "impacto": "Agrupación para imputación medianagrupal"
        },
        {
            "nombre": "Imputación Tiempo_Entrega_Real (mediana grupal)",
            "descripcion": "Llenar valores nulos con mediana del grupo Bodega-Ciudad",
            "variables_afectadas": ["Tiempo_Entrega_Real"],
            "tipo": "Imputación grupal",
            "codigo": """
df_transacciones['Tiempo_Entrega_Real'] = df_transacciones['Tiempo_Entrega_Real'].fillna(
    df_transacciones.groupby('id_tiempos_entrega')['Tiempo_Entrega_Real'].transform('median')
)
            """,
            "impacto": "Imputación contextualizada por ruta"
        },
        {
            "nombre": "Imputación Costo_Envio (mediana grupal)",
            "descripcion": "Llenar valores nulos con mediana del grupo Bodega-Ciudad",
            "variables_afectadas": ["Costo_Envio"],
            "tipo": "Imputación grupal",
            "codigo": """
df_transacciones['Costo_Envio'] = df_transacciones['Costo_Envio'].fillna(
    df_transacciones.groupby('id_tiempos_entrega')['Costo_Envio'].transform('median')
)
            """,
            "impacto": "Imputación contextualizada por ruta"
        },
        {
            "nombre": "Eliminación fila índice 0",
            "descripcion": "Remover primera fila (posible dato erróneo)",
            "variables_afectadas": ["Todas"],
            "tipo": "Limpieza",
            "codigo": "df_transacciones.drop(0, inplace=True)",
            "impacto": "Eliminación de fila problemática"
        },
        {
            "nombre": "Cálculo Fecha_Calculada",
            "descripcion": "Calcular fecha de entrega esperada",
            "variables_afectadas": ["Fecha_Calculada (nueva)"],
            "tipo": "Transformación",
            "codigo": "df_transacciones['Fecha_Calculada'] = df_transacciones.apply(lambda x: x['Fecha_Venta'] + pd.DateOffset(day=x['Tiempo_Entrega_Real']), axis=1)",
            "impacto": "Cálculo de fecha estimada de entrega"
        },
        {
            "nombre": "Imputación Estado_Envio (entregado)",
            "descripcion": "Marcar como 'ent.regado' si fecha calculada es anterior a fecha máxima",
            "variables_afectadas": ["Estado_Envio"],
            "tipo": "Imputación lógica",
            "codigo": """
fecha_max = df_transacciones.Fecha_Venta.max()
df_transacciones.loc[
    (df_transacciones['Fecha_Calculada'] < fecha_max) & (df_transacciones['Estado_Envio'].isna()),
    'Estado_Envio'
] = 'ent.regado'
            """,
            "impacto": "Inferencia de estado entregado"
        },
        {
            "nombre": "Imputación Estado_Envio (en tránsito)",
            "descripcion": "Marcar como 'en camino' si fecha calculada es posterior a fecha máxima",
            "variables_afectadas": ["Estado_Envio"],
            "tipo": "Imputación lógica",
            "codigo": """
df_transacciones.loc[
    (df_transacciones['Fecha_Calculada'] >= fecha_max) & (df_transacciones['Estado_Envio'].isna()),
    'Estado_Envio'
] = 'en camino'
            """,
            "impacto": "Inferencia de estado en tránsito"
        }
    ]
}

# ==========================================
# FUNCIÓN HELPER PARA VISUALIZACIÓN
# ==========================================
def get_all_cleaning_rules():
    """Retorna todas las reglas de limpieza en un formato unificado"""
    return [
        INVENTARIO_CLEANING_RULES,
        FEEDBACK_CLEANING_RULES,
        TRANSACCIONES_CLEANING_RULES
    ]
