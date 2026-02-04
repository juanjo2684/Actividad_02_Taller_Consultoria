# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
from src.data_loader import cargar_datos
from src.filtros import crear_sidebar_filtros
from src.paginas.resumen_ejecutivo import mostrar_resumen_ejecutivo
from src.paginas.fuga_capital import mostrar_fuga_capital
from src.paginas.crisis_logistica import mostrar_crisis_logistica
from src.paginas.venta_invisible import mostrar_venta_invisible
from src.paginas.diagnostico_fidelidad import mostrar_diagnostico_fidelidad
from src.paginas.riesgo_operativo import mostrar_riesgo_operativo

# -----------------------------
# 1. Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="TechLogistics DSS - Dashboard Ejecutivo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 2. Carga de datos centralizada
# -----------------------------
# El spinner solo aparecerá la primera vez gracias al cache en data_loader
try:
    df_dss, health_scores, metricas_calidad = cargar_datos()
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
    st.stop()

# -----------------------------
# 3. Sidebar y Filtros Globales
# -----------------------------
# Esta función ahora retorna el DF filtrado que usaremos en todas las tabs
df_filtrado = crear_sidebar_filtros(df_dss)

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar Datos Consolidados")

# Convertir el DataFrame a CSV (en memoria)
@st.cache_data
def convertir_df_a_csv(df):
    # Usamos utf-8-sig para que Excel abra bien las tildes en Windows
    return df.to_csv(index=False).encode('utf-8-sig')

csv_master = convertir_df_a_csv(df_filtrado)

st.sidebar.download_button(
    label="💾 Descargar Tabla Maestra (CSV)",
    data=csv_master,
    file_name=f"techlogistics_consolidado_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    help="Descarga los datos con filtros aplicados, uniones de tablas y cálculos de margen."
)

# -----------------------------
# 4. Título e Identidad Visual
# -----------------------------
st.title("📊 TechLogistics S.A.S")
st.markdown("### Sistema de Soporte a Decisiones (DSS) - Auditoría de Consultoría")
st.info(f"💡 **Base de Datos Actualizada:** Analizando {len(df_filtrado):,} transacciones filtradas.")

# -----------------------------
# 5. Navegación por Pestañas
# -----------------------------
tabs = st.tabs([
    "📈 Resumen Ejecutivo",
    "💰 Fuga de Capital",
    "🚚 Crisis Logística", 
    "👻 Venta Invisible",
    "⭐ Diagnóstico Fidelidad",
    "⚠️ Riesgo Operativo"
])

# Ruteo de funciones a cada pestaña
with tabs[0]:
    mostrar_resumen_ejecutivo(df_filtrado, health_scores, metricas_calidad)

with tabs[1]:
    mostrar_fuga_capital(df_filtrado)

with tabs[2]:
    mostrar_crisis_logistica(df_filtrado)

with tabs[3]:
    mostrar_venta_invisible(df_filtrado)

with tabs[4]:
    mostrar_diagnostico_fidelidad(df_filtrado)

with tabs[5]:
    mostrar_riesgo_operativo(df_filtrado)

# -----------------------------
# Footer
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.caption("© 2024 TechLogistics SAS - Dashboard de Auditoría Técnica")
