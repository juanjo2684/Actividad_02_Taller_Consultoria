# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

pd.set_option('future.no_silent_downcasting', True)

def procesar_feedback(ruta_csv):
    try:
        df_raw = pd.read_csv(ruta_csv)
    except Exception as e:
        return pd.DataFrame(), {"error": str(e)}

    df_feedback = df_raw.copy()
    
    # Limpieza agresiva de nombres de columnas
    df_feedback.columns = [c.strip() for c in df_feedback.columns]
    
    # Normalización de nombres
    mapeo = {
        'NPS': 'NPS_Numerico', 'Puntaje_NPS': 'NPS_Numerico', 'Satisfaccion': 'NPS_Numerico',
        'Ticket_Soporte_Abierto': 'Ticket_Soporte', 'Ticket_Abierto': 'Ticket_Soporte',
        'Soporte': 'Ticket_Soporte', 'Rating': 'Rating_Producto'
    }
    df_feedback = df_feedback.rename(columns=mapeo)

    # Asegurar columnas mínimas
    if 'NPS_Numerico' not in df_feedback.columns: df_feedback['NPS_Numerico'] = 5
    if 'Ticket_Soporte' not in df_feedback.columns: df_feedback['Ticket_Soporte'] = 'No'
    if 'Rating_Producto' not in df_feedback.columns: df_feedback['Rating_Producto'] = 3

    salud_antes = calcular_health_score(df_feedback)

    # Limpieza de valores
    df_feedback["NPS_Numerico"] = pd.to_numeric(df_feedback["NPS_Numerico"], errors='coerce').fillna(5)
    df_feedback["NPS_Categoria"] = df_feedback["NPS_Numerico"].apply(lambda x: "Promotor" if x >= 9 else ("Pasivo" if x >= 7 else "Detractor"))
    df_feedback["Rating_Producto"] = pd.to_numeric(df_feedback["Rating_Producto"], errors='coerce').fillna(3)
    df_feedback["Edad_Cliente"] = pd.to_numeric(df_feedback.get("Edad_Cliente", 35), errors='coerce').fillna(35)

    salud_despues = calcular_health_score(df_feedback)

    metricas = {
        "health_score_antes": salud_antes[0],
        "health_score_despues": salud_despues[0],
        "nps_promedio": df_feedback["NPS_Numerico"].mean()
    }

    return df_feedback, metricas

def calcular_health_score(df):
    if df.empty: return (0, 0, 0)
    total_celdas = df.size
    total_nulos = df.isna().sum().sum()
    porcentaje_nulos = total_nulos / total_celdas if total_celdas > 0 else 0
    duplicados = df.duplicated().sum()
    porcentaje_duplicados = duplicados / len(df) if len(df) > 0 else 0
    score = 100 * (1 - (0.7 * porcentaje_nulos + 0.3 * porcentaje_duplicados))
    return round(score, 2), round(porcentaje_nulos * 100, 2), round(porcentaje_duplicados * 100, 2)