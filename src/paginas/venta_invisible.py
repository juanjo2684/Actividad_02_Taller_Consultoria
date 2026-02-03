# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar_venta_invisible(df_filtrado):
    """
    Analiza el impacto financiero de ventas sin SKU en el maestro de inventario.
    Responde a la Pregunta Ejecutiva 3: Cuantificación de riesgo por falta de control.
    """
    st.header("👻 Análisis de la Venta Invisible")
    
    # 1. Segmentación de Datos
    df_sin_inv = df_filtrado[df_filtrado["venta_sin_inventario"]].copy()
    
    # KPIs de Impacto
    ingreso_riesgo = df_sin_inv["ingreso_total"].sum()
    pct_ingreso_riesgo = (ingreso_riesgo / df_filtrado["ingreso_total"].sum() * 100) if not df_filtrado.empty else 0
    skus_huerfanos = df_sin_inv["SKU_ID"].nunique()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Ingreso en Riesgo (USD)", f"${ingreso_riesgo:,.2f}", 
                  delta=f"{pct_ingreso_riesgo:.1f}% del Total", delta_color="inverse")
    with col2:
        st.metric("🆔 SKUs No Catalogados", f"{skus_huerfanos}")
    with col3:
        st.metric("📝 Transacciones Afectadas", f"{len(df_sin_inv):,}")

    st.markdown("---")

    # 2. Distribución Temporal del Descontrol
    st.subheader("📅 Evolución del Riesgo de Inventario")
    df_tiempo = df_sin_inv.groupby(df_sin_inv["Fecha_Venta"].dt.to_period("M")).agg({
        "ingreso_total": "sum",
        "Transaccion_ID": "count"
    }).reset_index()
    df_tiempo["Fecha_Venta"] = df_tiempo["Fecha_Venta"].astype(str)

    fig_line = px.line(df_tiempo, x="Fecha_Venta", y="ingreso_total", 
                      title="Ingresos por Ventas Invisibles a lo largo del tiempo",
                      labels={"ingreso_total": "Ingresos (USD)", "Fecha_Venta": "Mes"},
                      markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # 3. Análisis de Localización (Bodegas/Ciudades con más errores)
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📍 Fuga por Ciudad")
        fuga_ciudad = df_sin_inv.groupby("Ciudad_Destino")["ingreso_total"].sum().sort_values(ascending=False).head(10)
        fig_city = px.bar(fuga_ciudad, orientation='h', title="Top 10 Ciudades con Ventas Invisibles")
        st.plotly_chart(fig_city, use_container_width=True)
        
    with col_b:
        st.subheader("🏭 Impacto por Canal/Bodega")
        # Usamos Canal_Venta o Bodega_Origen según disponibilidad
        col_ref = "Canal_Venta" if "Canal_Venta" in df_sin_inv.columns else "Bodega_Origen"
        fuga_canal = df_sin_inv.groupby(col_ref)["ingreso_total"].sum().sort_values(ascending=False)
        fig_pie = px.pie(values=fuga_canal.values, names=fuga_canal.index, title=f"Distribución por {col_ref}")
        st.plotly_chart(fig_pie, use_container_width=True)

    # 4. Tabla de Auditoría Crítica
    st.subheader("🚨 Detalle de SKUs Fantasma (Top Impacto)")
    top_huerfanos = df_sin_inv.groupby("SKU_ID").agg({
        "Cantidad_Vendida": "sum",
        "ingreso_total": "sum",
        "Precio_Venta_Final": "mean"
    }).sort_values("ingreso_total", ascending=False).head(15)
    
    st.dataframe(top_huerfanos.style.format({"ingreso_total": "${:,.2f}", "Precio_Venta_Final": "${:,.2f}"}), 
                 use_container_width=True)

    # 5. Diagnóstico Ejecutivo
    with st.expander("💡 Conclusión del Consultor"):
        if pct_ingreso_riesgo > 10:
            st.error(f"⚠️ **ALERTA CRÍTICA:** El {pct_ingreso_riesgo:.1f}% de los ingresos no tiene trazabilidad de costo. Se esta operando a ciegas sobre el margen real de estos productos.")
        elif pct_ingreso_riesgo > 5:
            st.warning("🟡 **RIESGO MODERADO:** Existe una brecha de catalogación. Es probable que sean lanzamientos de productos nuevos no registrados en el sistema central.")
        else:
            st.success("✅ **RIESGO BAJO:** El nivel de SKUs huérfanos es ruido operativo mínimo.")