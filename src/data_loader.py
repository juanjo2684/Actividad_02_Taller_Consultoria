# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from src.inventario import procesar_inventario
from src.transacciones import procesar_transacciones
from src.feedback import procesar_feedback

pd.set_option('future.no_silent_downcasting', True)

@st.cache_data
def cargar_datos():
    # Carga de archivos individuales
    df_inv, met_inv = procesar_inventario("data/inventario_central_v2.csv")
    df_feed, met_feed = procesar_feedback("data/feedback_clientes_v2.csv")
    df_trans, met_trans = procesar_transacciones("data/transacciones_logistica_v2.csv", df_inv, df_feed)
    
    # Consolidación protegida
    df_dss = crear_dataset_consolidado(df_trans, df_inv, df_feed)
    
    health_scores = {
        "Inventario": {"Antes": met_inv.get("health_score_antes", 0), "Despues": met_inv.get("health_score_despues", 0)},
        "Transacciones": {"Antes": met_trans.get("health_score_antes", 0), "Despues": met_trans.get("health_score_despues", 0)},
        "Feedback": {"Antes": met_feed.get("health_score_antes", 0), "Despues": met_feed.get("health_score_despues", 0)}
    }
    
    metricas_calidad = {"inventario": met_inv, "transacciones": met_trans, "feedback": met_feed}
    return df_dss, health_scores, metricas_calidad

def crear_dataset_consolidado(df_trans, df_inv, df_feed):
    # 1. Asegurar Tiempo_Entrega en el dataframe de origen
    if 'Tiempo_Entrega' not in df_trans.columns:
        # Intento de rescate final por si el archivo tiene otro nombre no mapeado
        posibles = [c for c in df_trans.columns if 'tiempo' in c.lower() or 'entrega' in c.lower()]
        if posibles:
            df_trans = df_trans.rename(columns={posibles[0]: 'Tiempo_Entrega'})
        else:
            df_trans['Tiempo_Entrega'] = 0

    # 2. Cruce con Inventario
    df_merged = df_trans.merge(
        df_inv[['SKU_ID', 'Categoria', 'Costo_Unitario_USD', 'Punto_Reorden', 'Stock_Actual', 'Bodega_Origen', 'Lead_Time_Dias', 'Ultima_Revision']],
        on="SKU_ID", how="left"
    )
    
    # 3. Cruce con Feedback
    cols_feed = [c for c in ['Transaccion_ID', 'NPS_Numerico', 'NPS_Categoria', 'Rating_Producto', 'Edad_Cliente', 'Ticket_Soporte'] if c in df_feed.columns]
    
    df_final = df_merged.merge(
        df_feed[cols_feed].drop_duplicates(subset=['Transaccion_ID']),
        on="Transaccion_ID", how="left"
    )
    
    # 4. Rellenos de seguridad para que los cálculos no den NaN
    df_final["Categoria"] = df_final["Categoria"].fillna("No Catalogado")
    df_final["venta_sin_inventario"] = df_final["Categoria"] == "No Catalogado"
    df_final["NPS_Numerico"] = df_final["NPS_Numerico"].fillna(5)
    df_final["Stock_Actual"] = df_final["Stock_Actual"].fillna(0)
    df_final["Tiempo_Entrega"] = df_final["Tiempo_Entrega"].fillna(0)
    
    # 5. Cálculos Financieros
    df_final["ingreso_total"] = df_final["Precio_Venta_Final"] * df_final["Cantidad_Vendida"]
    costo_u = df_final["Costo_Unitario_USD"].fillna(0)
    df_final["costo_total"] = (costo_u * df_final["Cantidad_Vendida"]) + df_final["Costo_Envio"]
    df_final["margen_real"] = df_final["ingreso_total"] - df_final["costo_total"]
    
    # 6. Brecha Logística
    if "Lead_Time_Dias" in df_final.columns:
        df_final["brecha_entrega"] = df_final["Tiempo_Entrega"] - df_final["Lead_Time_Dias"].fillna(0)
    else:
        df_final["brecha_entrega"] = 0

    # 7. Paradoja de Fidelidad
    stock_q3 = df_final["Stock_Actual"].quantile(0.75) if len(df_final) > 0 else 0
    df_final["paradoja_fidelidad"] = (df_final["Stock_Actual"] > stock_q3) & (df_final["NPS_Numerico"] < 7)

    return df_final