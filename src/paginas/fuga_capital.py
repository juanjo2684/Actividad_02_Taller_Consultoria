# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def mostrar_fuga_capital(df_filtrado):
    """
    Analiza la fuga de capital por márgenes negativos.
    Responde a la Pregunta Ejecutiva 1 sobre fallas de precios vs volumen aceptable.
    """
    st.header("💰 Fuga de Capital y Rentabilidad")
    
    # 1. Identificación de Pérdidas
    # Usamos una copia para no afectar el dataframe original
    df_perdida = df_filtrado[df_filtrado["margen_real"] < 0].copy()
    total_fuga = df_perdida["margen_real"].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💸 Fuga Total (USD)", f"${abs(total_fuga):,.2f}", delta_color="inverse")
    with col2:
        st.metric("📦 SKUs en Pérdida", f"{df_perdida['SKU_ID'].nunique()}")
    with col3:
        ingresos_totales = df_filtrado["ingreso_total"].sum()
        impacto_ingresos = (abs(total_fuga) / ingresos_totales * 100) if ingresos_totales > 0 else 0
        st.metric("% Impacto sobre Ingresos", f"{impacto_ingresos:.2f}%")

    st.markdown("---")

    # 2. Visualización Estratégica: Matriz de Riesgo
    st.subheader("🔍 Análisis de Riesgo: ¿Volumen o Falla de Precio?")
    
    # Agrupamos por SKU
    df_sku_risk = df_filtrado.groupby(["SKU_ID", "Categoria"]).agg({
        "margen_real": "sum",
        "ingreso_total": "sum",
        "Cantidad_Vendida": "sum"
    }).reset_index()

    # --- CORRECCIÓN DE SEGURIDAD ---
    # Creamos una columna de tamaño que sea siempre positiva y sin ceros absolutos para evitar errores de Plotly
    df_sku_risk["size_burbuja"] = df_sku_risk["Cantidad_Vendida"].fillna(0).abs() + 0.1
    # -------------------------------

    fig_risk = px.scatter(
        df_sku_risk,
        x="ingreso_total",
        y="margen_real",
        size="size_burbuja",
        color="margen_real",
        color_continuous_scale="RdYlGn", # Verde para ganancias, Rojo para pérdidas
        color_continuous_midpoint=0,    # Forzamos que el blanco/amarillo sea el 0
        hover_name="SKU_ID",
        labels={"ingreso_total": "Ingresos Totales (USD)", "margen_real": "Margen Neto (USD)"},
        title="Matriz de Dispersión: Margen vs. Ingresos por SKU"
    )
    
    # Línea de referencia en 0 (Punto de equilibrio)
    fig_risk.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Punto de Equilibrio")
    st.plotly_chart(fig_risk, use_container_width=True)

    # 3. Análisis por Canal (Online vs Retail)
    st.subheader("🌐 Falla Crítica por Canal")
    
    canal_col = "Canal_Venta" if "Canal_Venta" in df_filtrado.columns else "Bodega_Origen"
    
    df_canal = df_filtrado.groupby(canal_col).agg({
        "margen_real": "sum",
        "ingreso_total": "sum"
    }).reset_index()
    
    # Evitar división por cero
    df_canal["%_Margen"] = df_canal.apply(lambda x: (x["margen_real"] / x["ingreso_total"] * 100) if x["ingreso_total"] > 0 else 0, axis=1)

    fig_canal = px.bar(
        df_canal,
        x=canal_col,
        y="%_Margen",
        color="%_Margen",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title="Rendimiento de Margen por Canal/Origen",
        text_auto=".2f"
    )
    st.plotly_chart(fig_canal, use_container_width=True)

    # 4. Listado de SKUs Críticos (Top 10 Fugas)
    st.subheader("🚨 Top 10 SKUs con Mayor Pérdida")
    if not df_perdida.empty:
        top_fugas = df_perdida.groupby("SKU_ID").agg({
            "Categoria": "first",
            "margen_real": "sum",
            "Cantidad_Vendida": "sum",
            "Precio_Venta_Final": "mean"
        }).sort_values("margen_real").head(10)
        
        st.table(top_fugas.style.format({
            "margen_real": "${:,.2f}", 
            "Precio_Venta_Final": "${:,.2f}",
            "Cantidad_Vendida": "{:,.0f}"
        }))
    else:
        st.success("No se detectaron SKUs con margen negativo en este filtro.")

    # 5. Recomendación de Consultoría
    with st.expander("💡 Diagnóstico del Consultor"):
        impacto = (abs(total_fuga) / ingresos_totales) if ingresos_totales > 0 else 0
        if impacto > 0.05:
            st.error(f"⚠️ **Falla Crítica detectada:** La fuga representa el {impacto*100:.2f}% de los ingresos. Esto sugiere una falla estructural en el algoritmo de precios o costos de envío no calculados.")
        elif total_fuga < 0:
            st.warning("⚠️ **Pérdida Controlada:** Los márgenes negativos están por debajo del 5%. Revisar si son productos gancho (loss-leaders).")
        else:
            st.success("✅ **Operación Saludable:** No hay fuga de capital significativa detectada.")