# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def mostrar_salud_dato(health_scores, metricas_calidad, metricas_limpieza):
    """
    Dashboard de salud de datos: muestra métricas de calidad y limpieza.
    """
    st.header("🔍 Salud del Dato - Auditoría de Calidad")
    st.markdown("---")
    
    # -----------------------------
    # Resumen ejecutivo
    # -----------------------------
    st.subheader("📊 Resumen Ejecutivo de Salud de Datos")
    
    # Calcular promedio de Health Score
    hs_promedio_antes = sum([v["Antes"] for v in health_scores.values()]) / len(health_scores)
    hs_promedio_despues = sum([v["Despues"] for v in health_scores.values()]) / len(health_scores)
    mejora_promedio = hs_promedio_despues - hs_promedio_antes
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⭐ Health Score Promedio (Antes)", 
                 f"{hs_promedio_antes:.1f}/100",
                 "BAJO" if hs_promedio_antes < 70 else "REGULAR" if hs_promedio_antes < 80 else "BUENO" if hs_promedio_antes < 90 else "EXCELENTE")
    
    with col2:
        st.metric("⭐ Health Score Promedio (Después)", 
                 f"{hs_promedio_despues:.1f}/100",
                 "BAJO" if hs_promedio_despues < 70 else "REGULAR" if hs_promedio_despues < 80 else "BUENO" if hs_promedio_despues < 90 else "EXCELENTE")
    
    with col3:
        st.metric("📈 Mejora Promedio", 
                 f"+{mejora_promedio:.1f} puntos",
                 f"{(mejora_promedio/hs_promedio_antes*100):.1f}%" if hs_promedio_antes > 0 else "0%")
    
    with col4:
        # Contar datasets con Health Score > 90
        datasets_excelentes = sum(1 for v in health_scores.values() if v["Despues"] >= 90)
        st.metric("🏆 Datasets Excelentes", 
                 f"{datasets_excelentes}/3",
                 "✅ TODOS" if datasets_excelentes == 3 else "⚠️ PARCIAL" if datasets_excelentes >= 1 else "❌ NINGUNO")
    
    st.markdown("---")
    
    # -----------------------------
    # Health Scores detallados
    # -----------------------------
    st.subheader("📈 Health Scores por Dataset")
    
    # Convertir a DataFrame
    hs_data = []
    for dataset, scores in health_scores.items():
        hs_data.append({
            "Dataset": dataset,
            "Antes": scores["Antes"],
            "Despues": scores["Despues"],
            "Mejora": scores["Despues"] - scores["Antes"]
        })
    
    df_hs = pd.DataFrame(hs_data)
    
    # Gráfico de barras agrupadas
    fig = px.bar(
        df_hs,
        x="Dataset",
        y=["Antes", "Despues"],
        barmode="group",
        title="Health Score: Comparativa Antes vs Después",
        labels={"value": "Health Score", "variable": "Estado"},
        color_discrete_map={"Antes": "#FF6B6B", "Despues": "#4ECDC4"}
    )
    
    # Añadir línea de umbral excelente (90)
    fig.add_hline(y=90, line_dash="dash", line_color="green", 
                 annotation_text="Umbral Excelente", annotation_position="bottom right")
    
    # Añadir línea de umbral aceptable (70)
    fig.add_hline(y=70, line_dash="dash", line_color="orange", 
                 annotation_text="Umbral Aceptable", annotation_position="bottom right")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla detallada
    st.dataframe(
        df_hs.style.format({
            "Antes": "{:.1f}",
            "Despues": "{:.1f}",
            "Mejora": "{:+.1f}"
        }).background_gradient(subset=["Mejora"], cmap="RdYlGn"),
        hide_index=True
    )
    
    st.markdown("---")
    
    # -----------------------------
    # Métricas de limpieza por dataset
    # -----------------------------
    st.subheader("🧹 Métricas de Limpieza por Dataset")
    
    tabs = st.tabs(["Feedback", "Inventario", "Transacciones"])
    
    with tabs[0]:
        if "Feedback" in metricas_limpieza:
            mostrar_metricas_feedback(metricas_limpieza["Feedback"])
    
    with tabs[1]:
        if "Inventario" in metricas_limpieza:
            mostrar_metricas_inventario(metricas_limpieza["Inventario"])
    
    with tabs[2]:
        if "Transacciones" in metricas_limpieza:
            mostrar_metricas_transacciones(metricas_limpieza["Transacciones"])
    
    st.markdown("---")
    
    # -----------------------------
    # Distribución de nulidad
    # -----------------------------
    st.subheader("📊 Distribución de Nulidad por Dataset")
    
    # Crear visualización de nulidad
    nulidad_data = []
    for dataset, metricas in metricas_calidad.items():
        if "nulidad_antes" in metricas and "nulidad_despues" in metricas:
            total_celdas_antes = sum(metricas["nulidad_antes"].values())
            total_celdas_despues = sum(metricas["nulidad_despues"].values())
            
            # Calcular porcentajes
            if total_celdas_antes > 0:
                pct_nulos_antes = (total_celdas_antes / (len(metricas["nulidad_antes"]) * metricas.get("registros_iniciales", 1))) * 100
                pct_nulos_despues = (total_celdas_despues / (len(metricas["nulidad_despues"]) * metricas.get("registros_finales", 1))) * 100
                
                nulidad_data.append({
                    "Dataset": dataset,
                    "Antes": pct_nulos_antes,
                    "Despues": pct_nulos_despues,
                    "Reducción": pct_nulos_antes - pct_nulos_despues
                })
    
    if nulidad_data:
        df_nulidad = pd.DataFrame(nulidad_data)
        
        fig = px.bar(
            df_nulidad,
            x="Dataset",
            y=["Antes", "Despues"],
            barmode="group",
            title="Porcentaje de Nulidad: Antes vs Despues",
            labels={"value": "% de Celdas Nulas", "variable": "Estado"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # -----------------------------
    # Detalle de decisiones de limpieza
    # -----------------------------
    st.subheader("📋 Detalle de Decisiones de Limpieza")
    
    # Mostrar decisiones clave
    st.markdown("""
    ### 🎯 Decisiones Clave de Curaduría:
    
    **1. Feedback de Clientes:**
    - ✅ Duplicados exactos eliminados: Redundancia pura sin valor analítico
    - ✅ Edades imposibles (195 años): Imputadas con mediana (18-90)
    - ✅ Valores NPS inconsistentes: Normalizados a escala 0-10
    
    **2. Inventario Central:**
    - ✅ Costos atípicos ($0.01 - $850k): Reemplazados con mediana por categoría
    - ✅ Stock negativo: Convertido a positivo (manteniendo magnitud del desajuste)
    - ✅ Lead times inconsistentes: Extraídos de strings y normalizados
    
    **3. Transacciones Logísticas:**
    - ✅ Tiempos de entrega extremos (999 días): Tratados como outliers e imputados
    - ✅ Cantidades negativas: Convertidas a positivos (devoluciones reales)
    - ✅ Costos de envío nulos: Imputados por mediana de ruta (bodega-ciudad)
    """)
    
    st.markdown("---")
    
    # -----------------------------
    # Exportar reportes
    # -----------------------------
    st.subheader("📤 Exportar Reportes de Calidad")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Reporte de Health Scores
        csv_hs = df_hs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Health Scores (CSV)",
            data=csv_hs,
            file_name="health_scores.csv",
            mime="text/csv"
        )
    
    with col2:
        # Reporte consolidado de métricas
        metricas_consolidadas = []
        for dataset, metricas in metricas_calidad.items():
            metricas_consolidadas.append({
                "Dataset": dataset,
                "Registros Iniciales": metricas.get("registros_iniciales", 0),
                "Registros Finales": metricas.get("registros_finales", 0),
                "Health Score Antes": health_scores.get(dataset, {}).get("Antes", 0),
                "Health Score Despues": health_scores.get(dataset, {}).get("Despues", 0),
                "Duplicados Eliminados": metricas.get("duplicados_eliminados", 0),
                "Outliers Corregidos": metricas.get("costos_outliers_detectados", 
                                                   metricas.get("edades_fuera_rango_corregidas", 0))
            })
        
        df_consolidado = pd.DataFrame(metricas_consolidadas)
        csv_cons = df_consolidado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Descargar Métricas Consolidadas (CSV)",
            data=csv_cons,
            file_name="metricas_calidad_consolidadas.csv",
            mime="text/csv"
        )
    
    with col3:
        # Reporte ejecutivo en PDF (simulado)
        st.info("El reporte ejecutivo completo se genera en la pestaña 'Resumen Ejecutivo'")
    
    st.markdown("---")
    
    # -----------------------------
    # Recomendaciones para mejora continua
    # -----------------------------
    st.subheader("🚀 Recomendaciones para Mejora Continua")
    
    # Identificar oportunidades de mejora
    oportunidades = []
    
    for dataset, scores in health_scores.items():
        if scores["Despues"] < 95:
            oportunidades.append(f"**{dataset}**: Health Score de {scores['Despues']:.1f}/100. Objetivo: alcanzar 95+")
    
    if oportunidades:
        st.warning("### ⚠️ Oportunidades de Mejora Identificadas:")
        for op in oportunidades:
            st.markdown(f"- {op}")
        
        st.markdown("""
        ### 📋 Plan de Mejora:
        1. **Implementar validaciones en tiempo real** en puntos de entrada de datos
        2. **Automatizar procesos de limpieza** con pipelines ETL programados
        3. **Establecer KPIs de calidad** por dataset y monitoreo mensual
        4. **Capacitar equipos** en mejores prácticas de captura de datos
        """)
    else:
        st.success("### 🎉 ¡Excelente! Todos los datasets tienen Health Score superior a 95/100")
        st.markdown("**Recomendaciones para mantener la calidad:**")
        st.markdown("""
        1. **Monitoreo proactivo** de métricas de calidad
        2. **Auditorías periódicas** (trimestrales) de datos
        3. **Documentación continua** de cambios en estructura de datos
        4. **Backup y versionado** de datasets procesados
        """)

# Funciones auxiliares para mostrar métricas específicas
def mostrar_metricas_feedback(metricas):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Duplicados Eliminados", metricas.get("duplicados_eliminados", 0))
    
    with col2:
        st.metric("👤 Edades Corregidas", metricas.get("edades_corregidas", 0))
    
    with col3:
        st.metric("⭐ NPS Válidos", metricas.get("nps_registros_validos", 0) 
                 if "nps_registros_validos" in metricas else "N/A")
    
    st.markdown("""
    **Decisiones aplicadas:**
    - Eliminación de duplicados exactos (redundancia pura)
    - Imputación de edades imposibles con mediana
    - Normalización de escala NPS a 0-10
    """)

def mostrar_metricas_inventario(metricas):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Outliers de Costo", metricas.get("costos_outliers", 0))
    
    with col2:
        st.metric("📦 Stock Negativos Corregidos", metricas.get("stock_negativos", 0))
    
    with col3:
        st.metric("🏷️ Categorías Normalizadas", "Todas")
    
    st.markdown("""
    **Decisiones aplicadas:**
    - Reemplazo de costos atípicos con mediana por categoría
    - Conversión de stock negativo a positivo (manteniendo magnitud)
    - Normalización de nombres de categorías
    - Extracción de lead times de strings inconsistentes
    """)

def mostrar_metricas_transacciones(metricas):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📦 Cantidades Negativas", metricas.get("cantidades_negativas", 0))
    
    with col2:
        st.metric("⏱️ Tiempos Outliers", metricas.get("tiempos_outliers", 0))
    
    with col3:
        st.metric("📊 SKUs Sin Inventario", metricas.get("skus_sin_inventario", 0) 
                 if "skus_sin_inventario" in metricas else "N/A")
    
    st.markdown("""
    **Decisiones aplicadas:**
    - Conversión de cantidades negativas a positivos (devoluciones)
    - Tratamiento de tiempos de entrega extremos (999 días)
    - Imputación contextual por ruta (bodega-ciudad)
    - Documentación de SKUs sin correspondencia en inventario
    """)