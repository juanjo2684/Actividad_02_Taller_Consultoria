import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from inventario import procesar_inventario
from feedback import clean_feedback_dataset
from transacciones import procesar_transacciones
from data_cleaning_rules import get_all_cleaning_rules


@st.cache_data
def load_data():
	inventario = procesar_inventario('inventario_central_v2.csv')
	feedback = clean_feedback_dataset('feedback_clientes_v2.csv')
	transacciones = procesar_transacciones('transacciones_logistica_v2.csv', inventario, feedback)
	return inventario, feedback, transacciones


def show_df_info(df):
	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric("📊 Filas", f"{df.shape[0]:,}")
	with col2:
		st.metric("📋 Columnas", df.shape[1])
	with col3:
		st.metric("💾 Tamaño (KB)", f"{df.memory_usage(deep=True).sum() / 1024:.1f}")
	
	st.subheader("Tipos de datos")
	dtypes_df = pd.DataFrame({
		'Columna': df.columns,
		'Tipo': df.dtypes.values
	})
	st.dataframe(dtypes_df, use_container_width=True, hide_index=True)
	
	st.subheader("Valores nulos por columna (%)")
	nulls = (df.isna().mean() * 100).round(2).sort_values(ascending=False)
	if nulls.sum() > 0:
		nulls_df = pd.DataFrame({
			'Columna': nulls.index,
			'Porcentaje': nulls.values
		})
		fig_nulls = px.bar(nulls_df, x='Porcentaje', y='Columna', orientation='h',
						title='Porcentaje de valores nulos',
						labels={'Porcentaje': 'Porcentaje (%)', 'Columna': ''})
		fig_nulls.update_layout(showlegend=False, height=max(300, len(nulls) * 20))
		st.plotly_chart(fig_nulls, use_container_width=True)
	else:
		st.success("✅ No hay valores nulos en este dataset")


# ==========================================
# FUNCIONES MODULARES - ANÁLISIS ESPECÍFICOS
# ==========================================

def show_transacciones_analysis(transacciones):
	"""Análisis detallado de transacciones: temporal, por canal y estado de envío"""
	df_time = transacciones.copy()
	df_time['Fecha_Venta'] = pd.to_datetime(df_time['Fecha_Venta'], errors='coerce')
	
	# Series temporal: Ventas por mes
	sales_monthly = df_time.groupby(df_time['Fecha_Venta'].dt.to_period('M')).agg({
		'Precio_Venta_Final': 'sum',
		'Cantidad_Vendida': 'sum',
		'Transaccion_ID': 'count'
	}).reset_index()
	sales_monthly['Fecha_Venta'] = sales_monthly['Fecha_Venta'].dt.to_timestamp()
	sales_monthly.rename(columns={
		'Precio_Venta_Final': 'Ventas Totales (USD)',
		'Cantidad_Vendida': 'Cantidad Total',
		'Transaccion_ID': 'Número de Transacciones'
	}, inplace=True)
	
	if not sales_monthly.empty:
		fig_series = px.line(sales_monthly, x='Fecha_Venta', y='Ventas Totales (USD)',
						markers=True, title='Ventas totales por mes',
						labels={'Fecha_Venta': 'Mes', 'Ventas Totales (USD)': 'Total (USD)'})
		fig_series.update_traces(line_color='#d62728', marker_size=8)
		st.plotly_chart(fig_series, use_container_width=True)
		
		# Métricas clave
		col1, col2, col3 = st.columns(3)
		with col1:
			st.metric("💰 Ventas totales", f"${sales_monthly['Ventas Totales (USD)'].sum():,.0f}")
		with col2:
			st.metric("📦 Cantidad vendida", f"{sales_monthly['Cantidad Total'].sum():,.0f}")
		with col3:
			st.metric("🔢 Total transacciones", f"{sales_monthly['Número de Transacciones'].sum():,.0f}")
	
	# Análisis por canal de venta
	if 'Canal_Venta' in transacciones.columns:
		st.subheader('💳 Análisis por canal de venta')
		canal_analysis = transacciones.groupby('Canal_Venta').agg({
			'Transaccion_ID': 'count',
			'Precio_Venta_Final': 'sum'
		}).reset_index()
		canal_analysis.columns = ['Canal', 'Número de Transacciones', 'Ventas Totales']
		
		fig_canal = px.bar(canal_analysis, x='Canal', y='Ventas Totales',
					 color='Canal', title='Ventas por canal de venta',
					 labels={'Ventas Totales': 'Total (USD)'})
		st.plotly_chart(fig_canal, use_container_width=True)
	
	# Análisis por estado de envío
	if 'Estado_Envio' in transacciones.columns:
		st.subheader('📦 Análisis por estado de envío')
		estado_analysis = transacciones['Estado_Envio'].value_counts()
		fig_estado = px.pie(values=estado_analysis.values, names=estado_analysis.index,
					 title='Distribución de estados de envío', hole=0.3)
		st.plotly_chart(fig_estado, use_container_width=True)


def show_inventario_analysis(inventario):
	"""Análisis detallado de inventario: categorías, bodegas, stock"""
	col1, col2 = st.columns(2)
	
	# Análisis por categoría
	with col1:
		st.subheader('📂 Distribución por categoría')
		cat_counts = inventario['Categoria'].value_counts()
		fig_cat = px.pie(values=cat_counts.values, names=cat_counts.index,
					title='Productos por categoría')
		st.plotly_chart(fig_cat, use_container_width=True)
	
	# Análisis por bodega
	with col2:
		st.subheader('🏭 Distribución por bodega')
		bodega_counts = inventario['Bodega_Origen'].value_counts()
		fig_bodega = px.bar(x=bodega_counts.index, y=bodega_counts.values,
					title='Cantidad de productos por bodega',
					labels={'x': 'Bodega', 'y': 'Cantidad'})
		st.plotly_chart(fig_bodega, use_container_width=True)
	
	# Stock actual
	st.subheader('📊 Análisis de Stock')
	stock_stats = inventario['Stock_Actual'].describe()
	col1, col2, col3, col4 = st.columns(4)
	
	with col1:
		st.metric("📈 Stock promedio", f"{stock_stats['mean']:.0f}")
	with col2:
		st.metric("📊 Stock mediano", f"{stock_stats['50%']:.0f}")
	with col3:
		st.metric("🔽 Stock mínimo", f"{stock_stats['min']:.0f}")
	with col4:
		st.metric("🔼 Stock máximo", f"{stock_stats['max']:.0f}")


def show_feedback_analysis(feedback):
	"""Análisis detallado de feedback: edad, recomendaciones, tickets de soporte"""
	col1, col2 = st.columns(2)
	
	# Distribución de edad
	with col1:
		st.subheader('👥 Distribución de edades')
		fig_age = px.histogram(feedback['Edad_Cliente'].dropna(), nbins=30,
						title='Distribución de edades de clientes',
						labels={'Edad_Cliente': 'Edad', 'count': 'Frecuencia'})
		fig_age.update_traces(marker_color='#1f77b4')
		st.plotly_chart(fig_age, use_container_width=True)
	
	# Recomendación de marca
	with col2:
		st.subheader('⭐ Recomendación de marca')
		recomienda_counts = feedback['Recomienda_Marca'].value_counts()
		fig_recomienda = px.pie(values=recomienda_counts.values, names=recomienda_counts.index,
						title='¿Recomendaría la marca?', hole=0.3)
		st.plotly_chart(fig_recomienda, use_container_width=True)
	
	# Tickets de soporte
	st.subheader('🎫 Estado de tickets de soporte')
	ticket_counts = feedback['Ticket_Soporte_Abierto'].value_counts()
	fig_ticket = px.bar(x=['Con Ticket', 'Sin Ticket'], 
				y=[ticket_counts.get(True, 0), ticket_counts.get(False, 0)],
				title='Distribución de tickets de soporte abiertos',
				labels={'x': 'Estado', 'y': 'Cantidad'})
	fig_ticket.update_traces(marker_color=['#ff6b6b', '#51cf66'])
	st.plotly_chart(fig_ticket, use_container_width=True)


def main():
	st.title('🔍 EDA Interactivo — Inventario / Feedback / Transacciones')
	
	# Sidebar con opciones de navegación
	st.sidebar.title("📋 Navegación")
	vista = st.sidebar.radio(
		"Selecciona la vista:",
		["📊 Exploración de Datos", "🧹 Reglas de Limpieza", "📈 Análisis Específico"]
	)

	# Cargar datos
	inventario, feedback, transacciones = load_data()

	# ==========================================
	# VISTA 1: EXPLORACIÓN DE DATOS
	# ==========================================
	if vista == "📊 Exploración de Datos":
		dataset = st.sidebar.selectbox(
			'Selecciona dataset',
			['Transacciones', 'Inventario', 'Feedback']
		)
		
		# Mapear selección a dataframe
		if dataset == 'Inventario':
			df = inventario
		elif dataset == 'Feedback':
			df = feedback
		else:
			df = transacciones

		st.header(f'{dataset}')
		
		# Tabs para organizar mejor la información
		tab1, tab2, tab3 = st.tabs(["👁️ Vista Previa", "📋 Información", "📊 Análisis"])
		
		with tab1:
			st.subheader('Vista rápida (primeras 5 filas)')
			st.dataframe(df.head(), use_container_width=True)
		
		with tab2:
			st.subheader('Resumen y calidad de datos')
			show_df_info(df)
		
		with tab3:
			# Análisis de variables numéricas
			num_cols = df.select_dtypes(include=['number']).columns.tolist()
			if num_cols:
				st.subheader('📊 Análisis de variables numéricas')
				
				st.write("**Estadísticas descriptivas:**")
				stats_df = df[num_cols].describe().T.round(2)
				st.dataframe(stats_df, use_container_width=True)
				
				col_num = st.selectbox('Visualizar distribución de:', num_cols, key='num_select')
				data_clean = df[col_num].dropna()
				
				# Histograma con media y mediana
				fig_hist = px.histogram(data_clean, nbins=50,
								title=f'Distribución de {col_num}',
								labels={col_num: col_num, 'count': 'Frecuencia'})
				fig_hist.update_traces(marker_color='#1f77b4')
				fig_hist.add_vline(x=data_clean.mean(), line_dash="dash", line_color="red",
							 annotation_text=f"Media: {data_clean.mean():.2f}")
				fig_hist.add_vline(x=data_clean.median(), line_dash="dash", line_color="green",
							 annotation_text=f"Mediana: {data_clean.median():.2f}")
				st.plotly_chart(fig_hist, use_container_width=True)
				
				# Box plot para outliers
				fig_box = px.box(df, y=col_num, title=f'Box plot - Detección de outliers: {col_num}')
				st.plotly_chart(fig_box, use_container_width=True)

			# Análisis de variables categóricas
			cat_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
			if cat_cols:
				st.subheader('🏷️ Análisis de variables categóricas')
				col_cat = st.selectbox('Visualizar conteos de:', cat_cols, key='cat_select')
				
				value_counts = df[col_cat].value_counts().head(15)
				fig_cat = px.bar(x=value_counts.values, y=value_counts.index,
							 orientation='h', title=f'Top 15 categorías en {col_cat}',
							 labels={'x': 'Conteo', 'y': col_cat})
				fig_cat.update_traces(marker_color='#2ca02c')
				st.plotly_chart(fig_cat, use_container_width=True)

		# Análisis adicional para Transacciones
		if dataset == 'Transacciones':
			st.subheader('📈 Análisis temporal')
			show_transacciones_analysis(transacciones)

	# ==========================================
	# VISTA 2: REGLAS DE LIMPIEZA
	# ==========================================
	elif vista == "🧹 Reglas de Limpieza":
		st.header("🧹 Documentación de Reglas de Limpieza de Datos")
		st.markdown("""
		Esta sección detalla todas las transformaciones y reglas de calidad aplicadas a cada dataset.
		Cada regla incluye: descripción, variables afectadas, tipo de operación y código ejecutado.
		""")
		
		# Seleccionar dataset para ver sus reglas
		dataset_rules = st.selectbox(
			"Selecciona un dataset para ver sus reglas:",
			['Inventario', 'Feedback', 'Transacciones'],
			key='rules_dataset'
		)
		
		# Obtener reglas
		all_rules = get_all_cleaning_rules()
		selected_rules = next(
			(r for r in all_rules if r["dataset"] == dataset_rules),
			None
		)
		
		if selected_rules:
			st.subheader(f"📋 {dataset_rules} - {len(selected_rules['rules'])} reglas de limpieza")
			
			# Crear tabs para cada regla
			for idx, rule in enumerate(selected_rules['rules'], 1):
				with st.expander(f"🔹 {idx}. {rule['nombre']}", expanded=(idx == 1)):
					col1, col2 = st.columns(2)
					
					with col1:
						st.markdown(f"**Descripción:**\n{rule['descripcion']}")
						st.markdown(f"**Tipo de operación:** `{rule['tipo']}`")
					
					with col2:
						st.markdown(f"**Variables afectadas:**")
						for var in rule['variables_afectadas']:
							st.markdown(f"- `{var}`")
					
					st.markdown("**Código ejecutado:**")
					st.code(rule['codigo'], language='python')
					
					st.markdown(f"**Impacto:** {rule['impacto']}")
					st.divider()

	# ==========================================
	# VISTA 3: ANÁLISIS ESPECÍFICO
	# ==========================================
	elif vista == "📈 Análisis Específico":
		st.header("📈 Análisis Específico por Dataset")
		
		analysis_type = st.selectbox(
			"Selecciona el análisis:",
			['Análisis de Transacciones', 'Análisis de Inventario', 'Análisis de Feedback']
		)
		
		if analysis_type == 'Análisis de Transacciones':
			st.subheader("💼 Análisis detallado de Transacciones")
			show_transacciones_analysis(transacciones)
		
		elif analysis_type == 'Análisis de Inventario':
			st.subheader("📦 Análisis detallado de Inventario")
			show_inventario_analysis(inventario)
		
		elif analysis_type == 'Análisis de Feedback':
			st.subheader("⭐ Análisis detallado de Feedback")
			show_feedback_analysis(feedback)


if __name__ == '__main__':
	main()