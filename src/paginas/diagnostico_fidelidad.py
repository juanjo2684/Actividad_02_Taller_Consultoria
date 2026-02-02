# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def mostrar_diagnostico_fidelidad(df_filtrado):
    """
    Analiza la paradoja de stock alto vs sentimiento negativo.
    Responde a la Pregunta Ejecutiva 4: ¿Calidad de producto o sobrecosto?
    """
    st.header("⭐ Diagnóstico de Fidelidad del Cliente")
    
    # 1. KPIs de Sentimiento
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nps_avg = df_filtrado["NPS_Numerico"].mean()
        st.metric("NPS Promedio", f"{nps_avg:.2f}/10")
    
    with col2:
        casos_paradoja = df_filtrado["paradoja_fidelidad"].sum()
        st.metric("📦 Casos de Paradoja", f"{casos_paradoja}", 
                  help="Productos con Stock Alto (>Q3) y NPS Bajo (<7)")
    
    with col3:
        rating_prod = df_filtrado["Rating_Producto"].mean()
        st.metric("⭐ Rating Producto", f"{rating_prod:.2f}/5")

    st.markdown("---")

    # 2. Análisis de Cuadrantes: Precio vs Calidad
    st.subheader("📊 Análisis de la Paradoja: ¿Por qué no se venden?")
    
    # Agrupamos por categoría para ver tendencias de sobrecosto
    df_cat = df_filtrado.groupby("Categoria").agg({
        "Precio_Venta_Final": "mean",
        "Rating_Producto": "mean",
        "Stock_Actual": "sum",
        "NPS_Numerico": "mean"
    }).reset_index()

    fig_bubble = px.scatter(
        df_cat,
        x="Rating_Producto",
        y="Precio_Venta_Final",
        size="Stock_Actual",
        color="NPS_Numerico",
        hover_name="Categoria",
        color_continuous_scale="RdYlGn",
        labels={"Rating_Producto": "Calidad (Rating)", "Precio_Venta_Final": "Precio Promedio (USD)"},
        title="Cuadrantes: Precio vs Calidad (Tamaño = Stock disponible)"
    )
    
    # Añadir líneas de referencia para crear cuadrantes
    fig_bubble.add_vline(x=df_cat["Rating_Producto"].mean(), line_dash="dot", line_color="gray")
    fig_bubble.add_hline(y=df_cat["Precio_Venta_Final"].mean(), line_dash="dot", line_color="gray")
    
    st.plotly_chart(fig_bubble, use_container_width=True)

    # 3. Zoom en Categorías con Paradoja
    st.subheader("🚨 Categorías en Zona de Riesgo")
    
    df_paradoja_resumen = df_filtrado[df_filtrado["paradoja_fidelidad"]].groupby("Categoria").agg({
        "Transaccion_ID": "count",
        "Stock_Actual": "mean",
        "NPS_Numerico": "mean",
        "ingreso_total": "sum"
    }).rename(columns={"Transaccion_ID": "Ventas Afectadas"}).sort_values("Ventas Afectadas", ascending=False)

    if not df_paradoja_resumen.empty:
        st.table(df_paradoja_resumen.style.format({
            "Stock_Actual": "{:.0f}",
            "NPS_Numerico": "{:.2f}",
            "ingreso_total": "${:,.2f}"
        }))
    else:
        st.success("No se detectan categorías con desalineación crítica entre stock y satisfacción.")

    # 4. Diagnóstico Detallado
    with st.expander("💡 Análisis del Consultor sobre la Paradoja"):
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write("**Hipótesis de Sobrecosto:**")
            st.info("Si el producto tiene buen Rating (>4) pero NPS bajo y stock alto, el problema es el **precio**. El cliente valora el producto pero no lo recomienda por su costo.")
            
        with col_right:
            st.write("**Hipótesis de Calidad:**")
            st.warning("Si el Rating es bajo (<3) y el stock es alto, el producto es **deficiente**. El stock se acumula porque el mercado ha rechazado la calidad del SKU.")

    # 5. Distribución de NPS
    st.subheader("📈 Distribución de Lealtad (NPS)")
    fig_nps = px.histogram(df_filtrado, x="NPS_Categoria", color="NPS_Categoria",
                          color_discrete_map={"Promotor": "green", "Pasivo": "yellow", "Detractor": "red"},
                          title="Volumen de Clientes por Categoría NPS")
    st.plotly_chart(fig_nps, use_container_width=True)