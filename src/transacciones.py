# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def procesar_transacciones(ruta_csv, df_inventario, df_feedback):
    """
    Carga y limpia el histórico de transacciones logísticas.
    """
    try:
        df_raw = pd.read_csv(ruta_csv)
    except Exception as e:
        return pd.DataFrame(), {"error": str(e)}

    df_trans = df_raw.copy()
    
    # 1. Limpieza de nombres de columnas (Quitar espacios invisibles)
    df_trans.columns = [c.strip() for c in df_trans.columns]
    
    # 2. ESTANDARIZACIÓN DE TIEMPO DE ENTREGA
    # Buscamos variantes comunes para evitar el KeyError
    mapeo_logistica = {
        'Tiempo_Entrega_Real': 'Tiempo_Entrega',
        'Dias_Entrega': 'Tiempo_Entrega',
        'Tiempo_Despacho': 'Tiempo_Entrega'
    }
    df_trans = df_trans.rename(columns=mapeo_logistica)
    
    # Si aún no existe, intentamos calcularla si hay fechas, o ponemos 0
    if 'Tiempo_Entrega' not in df_trans.columns:
        df_trans['Tiempo_Entrega'] = 0

    # Salud inicial
    salud_antes = calcular_health_score(df_trans)

    # 3. Limpieza de datos
    df_trans['Fecha_Venta'] = pd.to_datetime(df_trans['Fecha_Venta'], errors='coerce')
    df_trans['Tiempo_Entrega'] = pd.to_numeric(df_trans['Tiempo_Entrega'], errors='coerce').fillna(0)
    df_trans['Precio_Venta_Final'] = pd.to_numeric(df_trans['Precio_Venta_Final'], errors='coerce').fillna(0)
    df_trans['Costo_Envio'] = pd.to_numeric(df_trans['Costo_Envio'], errors='coerce').fillna(0)

    salud_despues = calcular_health_score(df_trans)

    metricas = {
        "health_score_antes": salud_antes[0],
        "health_score_despues": salud_despues[0],
        "total_transacciones": len(df_trans)
    }

    return df_trans, metricas

def calcular_health_score(df):
    if df.empty: return (0, 0, 0)
    total_celdas = df.size
    total_nulos = df.isna().sum().sum()
    porcentaje_nulos = total_nulos / total_celdas if total_celdas > 0 else 0
    duplicados = df.duplicated().sum()
    porcentaje_duplicados = duplicados / len(df) if len(df) > 0 else 0
    score = 100 * (1 - (0.7 * porcentaje_nulos + 0.3 * porcentaje_duplicados))
    return round(score, 2), round(porcentaje_nulos * 100, 2), round(porcentaje_duplicados * 100, 2)