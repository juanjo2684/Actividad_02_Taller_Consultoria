# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def procesar_transacciones(ruta_csv, df_inventario, df_feedback):
    """
    Carga, limpia y normaliza el histórico de transacciones.
    """
    try:
        df_raw = pd.read_csv(ruta_csv)
    except Exception as e:
        return pd.DataFrame(), {"error": str(e)}

    df_trans = df_raw.copy()
    
    # 1. Limpieza de nombres de columnas (Quita espacios en blanco invisibles)
    df_trans.columns = [c.strip() for c in df_trans.columns]
    
    # ---------------------------------------------------------
    # 2. ESTANDARIZACIÓN DIRECTA (Simplificada)
    # ---------------------------------------------------------
    # Como ya sabemos que el nombre oficial es 'Tiempo_Entrega_Real', 
    # lo unificamos a 'Tiempo_Entrega' para que el resto del sistema funcione.
    if 'Tiempo_Entrega_Real' in df_trans.columns:
        df_trans = df_trans.rename(columns={'Tiempo_Entrega_Real': 'Tiempo_Entrega'})
    elif 'Tiempo_Entrega' not in df_trans.columns:
        # Fallback de seguridad por si el archivo cambia en el futuro
        df_trans['Tiempo_Entrega'] = np.nan

    # ---------------------------------------------------------
    # 3. NORMALIZACIÓN DE CIUDADES (Consolidada)
    # ---------------------------------------------------------
    if 'Ciudad_Destino' in df_trans.columns:
        df_trans['Ciudad_Destino'] = df_trans['Ciudad_Destino'].astype(str).str.upper().str.strip()
        
        mapeo_ciudades = {
            "BOG": "BOGOTÁ", "BOGOTA": "BOGOTÁ",
            "MED": "MEDELLÍN", "MEDELLIN": "MEDELLÍN",
            "BAQ": "BARRANQUILLA", "BARRANQUILLA": "BARRANQUILLA",
            "VENTAS_WEB": "CANAL DIGITAL"
        }
        df_trans['Ciudad_Destino'] = df_trans['Ciudad_Destino'].replace(mapeo_ciudades)

    # 4. Limpieza de Tipos y Outliers
    df_trans['Fecha_Venta'] = pd.to_datetime(df_trans['Fecha_Venta'], errors='coerce')
    
    # Convertimos a numérico y gestionamos el outlier '999' detectado en el CSV maestro
    df_trans['Tiempo_Entrega'] = pd.to_numeric(df_trans['Tiempo_Entrega'], errors='coerce')
    df_trans.loc[df_trans['Tiempo_Entrega'] > 100, 'Tiempo_Entrega'] = np.nan 

    df_trans['Precio_Venta_Final'] = pd.to_numeric(df_trans['Precio_Venta_Final'], errors='coerce').fillna(0)
    df_trans['Costo_Envio'] = pd.to_numeric(df_trans['Costo_Envio'], errors='coerce').fillna(0)

    # Métricas de salud (asumiendo que calcular_health_score está definida abajo)
    salud_antes = (100, 0, 0) # Placeholder o llamada a tu función
    salud_despues = (100, 0, 0)

    metricas = {
        "health_score_antes": salud_antes[0],
        "health_score_despues": salud_despues[0],
        "total_transacciones": len(df_trans)
    }

    return df_trans, metricas