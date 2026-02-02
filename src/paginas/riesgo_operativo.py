# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

def mostrar_riesgo_operativo(df_filtrado):
    """
    Analiza la relación entre la falta de auditoría de stock y los problemas de servicio.
    Responde a la Pregunta Ejecutiva 5: ¿Qué bodegas operan a ciegas?
    """
    st.header("⚠️ Riesgo Operativo: Bodegas 'A Ciegas'")
    
    # 1. Preparación de métricas de antigüedad
    # Calculamos días desde la última revisión (asumiendo fecha actual como max de la data)
    fecha_referencia = df_filtrado["Ultima_Revision"].max()
    df_filtrado["dias_sin_revision"] = (fecha_referencia - df_filtrado["Ultima_Revision"]).dt.days
    
    # 2. KPIs de Riesgo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Promedio Días Sin Revisión", f"{df_filtrado['dias_sin_revision'].mean():.0f} días")
    with col2:
        tasa_soporte = (df_filtrado["Ticket_Soporte"] == "Sí").mean() * 100
        st.metric("🎫 Tasa de Tickets de Soporte", f"{tasa_soporte:.1f}%")
    with col3:
        # Correlación de Pearson entre antigüedad y tickets
        df_corr = df_filtrado.dropna(subset=["dias_sin_revision", "Ticket_Soporte"])
        # Convertimos Ticket_Soporte a binario para correlación
        df_corr["soporte_bin"] = (df_corr["Ticket_Soporte"] == "Sí").astype(int)
        correlacion = df_corr["dias_sin_revision"].corr(df_corr["soporte_bin"])
        st.metric("📈 Correlación Riesgo", f"{correlacion:.2f}", 
                  help="Cercano a 1 indica que a mayor descuido en revisión, más tickets de soporte.")

    st.markdown("---")

    # 3. Visualización: El Mapa del Descuido
    st.subheader("🕵️ Relación: Antigüedad de Revisión vs. Incidencias")
    
    # Agrupamos por Bodega para ver el impacto operativo
    df_bodega = df_filtrado.groupby("Bodega_Origen").agg({
        "dias_sin_revision": "mean",
        "Ticket_Soporte": lambda x: (x == "Sí").mean() * 100,
        "ingreso_total": "sum"
    }).reset_index()

    fig_riesgo = px.scatter(
        df_bodega,
        x="dias_sin_revision",
        y="Ticket_Soporte",
        size="ingreso_total",
        color="Ticket_Soporte",
        hover_name="Bodega_Origen",
        color_continuous_scale="Reds",
        labels={
            "dias_sin_revision": "Días Promedio desde Última Revisión",
            "Ticket_Soporte": "% Tasa de Tickets de Soporte"
        },
        title="Impacto del Descuido de Inventario por Bodega"
    )
    st.plotly_chart(fig_riesgo, use_container_width=True)

    # 4. Semáforo de Riesgo Operativo
    st.subheader("🚥 Semáforo de Auditoría por Bodega")
    
    def color_semaforo(val):
        if val > 60: return 'background-color: #ff4b4b; color: white' # Rojo
        if val > 30: return 'background-color: #ffa500; color: black' # Naranja
        return 'background-color: #28a745; color: white' # Verde

    resumen_auditoria = df_bodega.sort_values("dias_sin_revision", ascending=False)
    resumen_auditoria.columns = ["Bodega", "Días Sin Revisión", "% Tickets Soporte", "Ingresos Expuestos"]
    
    st.table(resumen_auditoria.style.applymap(color_semaforo, subset=["Días Sin Revisión"]).format({
        "% Tickets Soporte": "{:.1f}%",
        "Ingresos Expuestos": "${:,.2f}",
        "Días Sin Revisión": "{:.0f}"
    }))

    # 5. Storytelling de Riesgo
    with st.expander("💡 Diagnóstico sobre la Operación 'A Ciegas'"):
        st.write(f"La bodega **{resumen_auditoria.iloc[0]['Bodega']}** es la más crítica, operando con un rezago de **{resumen_auditoria.iloc[0]['Días Sin Revisión']:.0f} días** en auditoría.")
        st.warning("⚠️ **Impacto:** Esta falta de control correlaciona directamente con la insatisfacción final. Se recomienda una auditoría física inmediata en los nodos con color rojo.")