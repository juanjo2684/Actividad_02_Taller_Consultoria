# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def mostrar_crisis_logistica(df_filtrado):
    """
    Analiza la crisis logística y detecta rutas críticas.
    Responde a la Pregunta Ejecutiva 2: ¿Dónde cambiar de operador?
    """
    st.header("🚚 Crisis Logística y Cuellos de Botella")
    
    # ---------------------------------------------------------
    # 1. Preparación de Datos (FILTRO INTELIGENTE)
    # ---------------------------------------------------------
    # A. Quitamos nulos
    df_log = df_filtrado.dropna(subset=["Tiempo_Entrega", "NPS_Numerico"]).copy()
    
    # B. Filtramos los "falsos positivos" (NPS 5.0 por defecto) y tiempos irreales (outliers como 999)
    # Esto permite que la correlación sea matemáticamente calculable
    df_analisis = df_log[
        (df_log["NPS_Numerico"] != 5.0) & 
        (df_log["Tiempo_Entrega"] < 100) & 
        (df_log["Tiempo_Entrega"] > 0)
    ].copy()

    # Si después del filtro nos quedamos sin datos, usamos el dataframe original 
    # pero al menos quitamos los outliers de tiempo para no romper el gráfico
    if df_analisis.empty:
        df_analisis = df_log[df_log["Tiempo_Entrega"] < 100].copy()

    # ---------------------------------------------------------
    # 2. KPIs de Desempeño Logístico
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        tiempo_avg = df_analisis["Tiempo_Entrega"].mean()
        st.metric("⏳ Tiempo Entrega Prom.", f"{tiempo_avg:.1f} días")
    with col2:
        # Correlación Global
        corr_global = df_analisis["Tiempo_Entrega"].corr(df_analisis["NPS_Numerico"])
        st.metric("🔗 Correlación NPS vs Tiempo", f"{corr_global:.2f}" if not np.isnan(corr_global) else "N/A", 
                  help="Valores cercanos a -1 indican que a mayor tiempo, menor satisfacción.")
    with col3:
        brecha_max = df_analisis["brecha_entrega"].max() if "brecha_entrega" in df_analisis.columns else 0
        st.metric("🚩 Brecha Máxima", f"{brecha_max:.0f} días")

    st.markdown("---")

    # 3. Identificación de la Zona Crítica (Heatmap)
    st.subheader("📍 Mapa de Calor: ¿En qué ruta fallamos?")
    
    df_rutas = df_analisis.groupby(["Bodega_Origen", "Ciudad_Destino"]).agg({
        "NPS_Numerico": "mean",
        "Tiempo_Entrega": "mean",
        "Transaccion_ID": "count"
    }).reset_index()

    df_rutas["score_crisis"] = df_rutas["Tiempo_Entrega"] / (df_rutas["NPS_Numerico"] + 0.1)

    fig_heat = px.density_heatmap(
        df_rutas, 
        x="Ciudad_Destino", 
        y="Bodega_Origen", 
        z="score_crisis",
        color_continuous_scale="Reds",
        title="Intensidad de Crisis por Ruta",
        labels={"score_crisis": "Índice de Crisis"}
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # 4. Análisis de Correlación por Ciudad (EL GRÁFICO QUE APARECÍA VACÍO)
    st.subheader("📉 Correlación Específica por Ciudad")
    
    correlaciones_ciudad = []
    # Reducimos el requisito a > 2 registros para ver más datos en el gráfico
    for ciudad in df_analisis["Ciudad_Destino"].unique():
        df_c = df_analisis[df_analisis["Ciudad_Destino"] == ciudad]
        if len(df_c) >= 2: 
            corr = df_c["Tiempo_Entrega"].corr(df_c["NPS_Numerico"])
            if not np.isnan(corr):
                correlaciones_ciudad.append({"Ciudad": ciudad, "Correlacion": corr})
    
    if correlaciones_ciudad:
        df_corr_city = pd.DataFrame(correlaciones_ciudad).sort_values("Correlacion")

        fig_corr = px.bar(
            df_corr_city, 
            x="Correlacion", 
            y="Ciudad", 
            orientation='h',
            color="Correlacion",
            color_continuous_scale="RdYlGn_r",
            title="Ciudades donde el Tiempo afecta el NPS"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("⚠️ No hay suficiente variación en los datos de NPS para calcular correlaciones por ciudad. Se requiere mayor diversidad en las encuestas de satisfacción reales.")

    # 5. Recomendación Ejecutiva
    st.subheader("🚨 Recomendación de Intervención")
    if not df_rutas.empty:
        ruta_peor = df_rutas.sort_values("score_crisis", ascending=False).iloc[0]
        with st.expander("📝 Dictamen del Consultor Logístico"):
            st.error(f"Priorizar auditoría en ruta: **{ruta_peor['Bodega_Origen']} ➔ {ruta_peor['Ciudad_Destino']}**.")
            st.write(f"- **Tiempo prom.:** {ruta_peor['Tiempo_Entrega']:.1f} días.")
            st.info("Nota: La correlación indica qué tan sensibles son los clientes al tiempo en esta zona.")