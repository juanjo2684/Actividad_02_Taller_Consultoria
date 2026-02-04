# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def mostrar_diagnostico_fidelidad(df_filtrado):

    st.header("⭐ Diagnóstico de Fidelidad del Cliente")
    
    # 1. KPIs de Sentimiento
    # Estos ahora incluyen los NPS 5.0, dando una visión real del promedio global.
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nps_avg = df_filtrado["NPS_Numerico"].mean()
        st.metric("NPS Promedio", f"{nps_avg:.2f}/10", 
                  help="Promedio global incluyendo todas las calificaciones validadas.")
    
    with col2:
        casos_paradoja = df_filtrado["paradoja_fidelidad"].sum()
        st.metric("📦 Casos de Paradoja", f"{casos_paradoja}", 
                  help="Productos con Stock Alto (>Q3) y NPS Bajo (<7). Incluye los registros de NPS 5.0.")
    
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

    # El color ahora mostrará de forma más realista las categorías "tibias" (amarillo/naranja) 
    # debido a la presencia de los NPS 5.0.
    fig_bubble = px.scatter(
        df_cat,
        x="Rating_Producto",
        y="Precio_Venta_Final",
        size="Stock_Actual",
        color="NPS_Numerico",
        hover_name="Categoria",
        color_continuous_scale="RdYlGn",
        range_color=[0, 10], # Forzamos escala de 0 a 10 para ver el impacto real
        labels={"Rating_Producto": "Calidad (Rating)", "Precio_Venta_Final": "Precio Promedio (USD)", "NPS_Numerico": "NPS Avg"},
        title="Cuadrantes: Precio vs Calidad (Tamaño = Stock disponible)"
    )
    
    # Añadir líneas de referencia para crear cuadrantes
    fig_bubble.add_vline(x=df_cat["Rating_Producto"].mean(), line_dash="dot", line_color="gray")
    fig_bubble.add_hline(y=df_cat["Precio_Venta_Final"].mean(), line_dash="dot", line_color="gray")
    
    st.plotly_chart(fig_bubble, use_container_width=True)

    # 3. Zoom en Categorías con Paradoja
    st.subheader("🚨 Categorías en Zona de Riesgo")
    
    # Aquí se listarán las categorías donde los NPS 5.0 están "estancando" el inventario
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
            st.info("Si el producto tiene buen Rating (>4) pero NPS bajo (como los 5.0 detectados) y stock alto, el problema es el **precio**. El cliente está satisfecho con el objeto pero no con el valor percibido.")
            
        with col_right:
            st.write("**Hipótesis de Calidad:**")
            st.warning("Si el Rating es bajo (<3) y el stock es alto, el producto es **deficiente**. El inventario no rota porque la experiencia de uso es mala.")

    # 5. Distribución de NPS
    st.subheader("📈 Distribución de Lealtad (NPS)")
    
    # Al incluir los 5.0, la columna de 'Detractor' o 'Pasivo' crecerá significativamente,
    # mostrando el volumen real de clientes que no están promoviendo la marca.
    fig_nps = px.histogram(df_filtrado, x="NPS_Categoria", color="NPS_Categoria",
                          category_orders={"NPS_Categoria": ["Promotor", "Pasivo", "Detractor"]},
                          color_discrete_map={"Promotor": "#2ecc71", "Pasivo": "#f1c40f", "Detractor": "#e74c3c"},
                          title="Volumen Real de Clientes por Categoría (Incluye NPS 5.0)")
    
    st.plotly_chart(fig_nps, use_container_width=True)