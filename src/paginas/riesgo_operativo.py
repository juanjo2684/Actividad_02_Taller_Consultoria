# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

def mostrar_riesgo_operativo(df_filtrado):

    st.header("⚠️ Riesgo Operativo: Bodegas 'A Ciegas'")
    
    # 1. Preparación de métricas de antigüedad
    df_filtrado["Ultima_Revision"] = pd.to_datetime(df_filtrado["Ultima_Revision"])
    # La fecha de referencia debe ser hoy o la máxima del dataset para medir el rezago actual
    fecha_referencia = pd.to_datetime(datetime.now().date())
    df_filtrado["dias_sin_revision"] = (fecha_referencia - df_filtrado["Ultima_Revision"]).dt.days
    
    # 2. KPIs de Riesgo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        promedio_dias = df_filtrado['dias_sin_revision'].mean()
        st.metric("📅 Promedio Días Sin Revisión", f"{promedio_dias:.0f} días")
    
    with col2:
        # Tasa de tickets: Promedio de la columna binaria (0 y 1)
        tasa_soporte = df_filtrado["Ticket_Soporte"].mean() * 100
        st.metric("🎫 Tasa de Tickets de Soporte", f"{tasa_soporte:.1f}%")
        
    with col3:
        # IMPACTO DE LA CORRECCIÓN: Correlación con NPS completo (incluyendo 5.0)
        df_corr = df_filtrado.dropna(subset=["dias_sin_revision", "NPS_Numerico"])
        correlacion = df_corr["dias_sin_revision"].corr(df_corr["NPS_Numerico"])
        st.metric("📈 Correlación Riesgo/NPS", f"{correlacion:.2f}", 
                  help="Mide si el aumento en días sin revisión baja el NPS. Incluye los NPS 5.0 para mayor precisión estadística.")

    st.markdown("---")

    # 3. Visualización: El Mapa del Descuido
    st.subheader("🕵️ Relación: Antigüedad de Revisión vs. Incidencias")
    
    df_bodega = df_filtrado.groupby("Bodega_Origen").agg({
        "dias_sin_revision": "mean",
        "Ticket_Soporte": lambda x: x.mean() * 100,
        "ingreso_total": "sum",
        "NPS_Numerico": "mean" # Añadimos NPS promedio por bodega para el hover
    }).reset_index()

    fig_riesgo = px.scatter(
        df_bodega,
        x="dias_sin_revision",
        y="Ticket_Soporte",
        size="ingreso_total",
        color="Ticket_Soporte",
        hover_name="Bodega_Origen",
        hover_data={"NPS_Numerico": ":.2f"},
        color_continuous_scale="Reds",
        labels={
            "dias_sin_revision": "Días desde Última Revisión",
            "Ticket_Soporte": "% Tasa Soporte",
            "NPS_Numerico": "NPS Promedio"
        },
        title="Impacto del Descuido Operativo por Bodega"
    )
    st.plotly_chart(fig_riesgo, use_container_width=True)

    # 4. Semáforo de Riesgo Operativo
    st.subheader("🚥 Semáforo de Auditoría por Bodega")
    
    # Nota: applymap está siendo depurado en pandas nuevos, usamos map en el Styler
    def color_semaforo(val):
        if val > 60: return 'background-color: #ff4b4b; color: white' # Crítico (Rojo)
        if val > 30: return 'background-color: #ffa500; color: black' # Advertencia (Naranja)
        return 'background-color: #28a745; color: white' # Controlado (Verde)

    resumen_auditoria = df_bodega.sort_values("dias_sin_revision", ascending=False)
    # Seleccionamos columnas relevantes para la tabla
    tabla_final = resumen_auditoria[["Bodega_Origen", "dias_sin_revision", "Ticket_Soporte", "ingreso_total"]]
    tabla_final.columns = ["Bodega", "Días Sin Revisión", "% Tickets Soporte", "Ingresos Expuestos"]
    
    st.table(tabla_final.style.map(color_semaforo, subset=["Días Sin Revisión"]).format({
        "% Tickets Soporte": "{:.1f}%",
        "Ingresos Expuestos": "${:,.2f}",
        "Días Sin Revisión": "{:.0f}"
    }))

    # 5. Storytelling de Riesgo
    if not tabla_final.empty:
        with st.expander("💡 Diagnóstico sobre la Operación 'A Ciegas'"):
            peor_bodega = tabla_final.iloc[0]
            st.write(f"La bodega **{peor_bodega['Bodega']}** presenta el mayor riesgo operativo.")
            st.write(f"Tiene un rezago de **{peor_bodega['Días Sin Revisión']:.0f} días** sin auditoría, lo que coincide con una tasa de soporte del **{peor_bodega['% Tickets Soporte']}**.")
