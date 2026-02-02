# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from src.reportes import generar_reporte_ejecutivo_pdf

def mostrar_resumen_ejecutivo(df_filtrado, health_scores, metricas_calidad):
    """
    Muestra el resumen ejecutivo con KPIs clave.
    """
    st.header("📈 Resumen Ejecutivo")
    st.markdown("---")
    
    # -----------------------------
    # KPIs principales en 4 columnas
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ingresos_totales = df_filtrado["ingreso_total"].sum()
        st.metric("💰 Ingresos Totales", f"${ingresos_totales:,.0f}")
    
    with col2:
        margen_total = df_filtrado["margen_real"].sum()
        margen_pct = (margen_total / ingresos_totales * 100) if ingresos_totales != 0 else 0
        st.metric("📊 Margen Neto", f"${margen_total:,.0f}", f"{margen_pct:.1f}%")
    
    with col3:
        ventas_sin_inventario = df_filtrado["venta_sin_inventario"].sum()
        pct_riesgo = (ventas_sin_inventario / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
        st.metric("👻 Ventas Sin Inventario", ventas_sin_inventario, f"{pct_riesgo:.1f}%")
    
    with col4:
        margen_negativo = (df_filtrado["margen_real"] < 0).sum()
        st.metric("🔴 Transacciones con Perdida", margen_negativo)
    
    st.markdown("---")
    
    # -----------------------------
    # Health Scores
    # -----------------------------
    st.subheader("📊 Health Score de Datos")
    
    # Convertir health_scores a DataFrame para visualización
    hs_data = []
    for dataset, scores in health_scores.items():
        hs_data.append({
            "Dataset": dataset,
            "Antes": scores["Antes"],
            "Despues": scores["Despues"],
            "Mejora": scores["Despues"] - scores["Antes"]
        })
    
    df_hs = pd.DataFrame(hs_data)
    
    # Mostrar como tabla
    st.dataframe(df_hs.style.format({
        "Antes": "{:.1f}",
        "Despues": "{:.1f}",
        "Mejora": "{:+.1f}"
    }), hide_index=True)
    
    # Grafico de barras - CONVERTIR A FORMATO LARGO (melted)
    df_hs_melted = df_hs.melt(
        id_vars=["Dataset"], 
        value_vars=["Antes", "Despues"],
        var_name="Estado",
        value_name="Score"
    )
    
    fig_hs = px.bar(
        df_hs_melted,
        x="Dataset",
        y="Score",
        color="Estado",
        barmode="group",
        title="Health Score: Antes vs Despues de la Limpieza",
        labels={"Score": "Health Score", "Estado": "Estado"},
        color_discrete_map={"Antes": "red", "Despues": "green"}
    )
    
    st.plotly_chart(fig_hs, use_container_width=True)
    
    st.markdown("---")
    
    # -----------------------------
    # Top categorias por ingresos
    # -----------------------------
    st.subheader("🏆 Top Categorias por Ingresos")
    
    top_categorias = df_filtrado.groupby("Categoria").agg({
        "ingreso_total": "sum",
        "margen_real": "sum",
        "Transaccion_ID": "count"
    }).rename(columns={
        "ingreso_total": "Ingresos",
        "margen_real": "Margen",
        "Transaccion_ID": "Transacciones"
    }).nlargest(5, "Ingresos")
    
    top_categorias["Margen %"] = (top_categorias["Margen"] / top_categorias["Ingresos"] * 100).round(1)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_cat = px.bar(
            top_categorias.reset_index(),
            x="Categoria",
            y="Ingresos",
            color="Margen %",
            color_continuous_scale="RdYlGn",
            title="Top 5 Categorias por Ingresos"
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        st.dataframe(
            top_categorias[["Ingresos", "Margen %", "Transacciones"]].style.format({
                "Ingresos": "${:,.0f}",
                "Margen %": "{:.1f}%",
                "Transacciones": "{:,.0f}"
            }),
            height=400
        )
    
    st.markdown("---")
    
    # -----------------------------
    # Exportar reporte
    # -----------------------------
    st.subheader("📤 Exportar Reporte Ejecutivo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Exportar datos filtrados a CSV
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos Filtrados (CSV)",
            data=csv,
            file_name="datos_filtrados.csv",
            mime="text/csv"
        )
    
    with col2:
        # Exportar metricas a CSV
        metricas_df = pd.DataFrame(metricas_calidad).T
        csv_metricas = metricas_df.to_csv().encode('utf-8')
        st.download_button(
            label="📊 Descargar Metricas (CSV)",
            data=csv_metricas,
            file_name="metricas_calidad.csv",
            mime="text/csv"
        )
    
    with col3:
        # Generar y descargar PDF ejecutivo
        if st.button("📄 Generar Reporte Ejecutivo (PDF)"):
            with st.spinner("Generando PDF..."):
                pdf_buffer = generar_reporte_ejecutivo_pdf(
                    df_filtrado, 
                    health_scores, 
                    metricas_calidad
                )
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_buffer,
                    file_name="Reporte_Ejecutivo_TechLogistics.pdf",
                    mime="application/pdf"
                )
    
    st.markdown("---")
    st.info("💡 **Nota:** Este dashboard se actualiza automaticamente con los filtros aplicados en el panel izquierdo.")