import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from inventario import procesar_inventario
from feedback import clean_feedback_dataset
from transacciones import procesar_transacciones


@st.cache_data
def load_data():
	inventario = procesar_inventario('inventario_central_v2.csv')
	feedback = clean_feedback_dataset('feedback_clientes_v2.csv')
	transacciones = procesar_transacciones('transacciones_logistica_v2.csv', inventario, feedback)
	return inventario, feedback, transacciones


def show_df_info(df):
	st.write('Filas:', df.shape[0], ' — Columnas:', df.shape[1])
	st.write(df.dtypes)
	nulls = (df.isna().mean() * 100).round(2).sort_values(ascending=False)
	st.write(nulls)


def main():
	st.title('EDA interactivo — Inventario / Feedback / Transacciones')

	inventario, feedback, transacciones = load_data()

	dataset = st.sidebar.selectbox('Selecciona dataset', ['Transacciones', 'Inventario', 'Feedback'])
	if dataset == 'Inventario':
		df = inventario
	elif dataset == 'Feedback':
		df = feedback
	else:
		df = transacciones

	st.header(dataset)
	st.subheader('Vista rápida')
	st.dataframe(df.head())

	st.subheader('Resumen y calidad')
	show_df_info(df)

	st.subheader('Proporción de valores nulos por columna (%)')
	nulls = (df.isna().mean() * 100).sort_values(ascending=False)
	st.bar_chart(nulls)

	num_cols = df.select_dtypes(include=['number']).columns.tolist()
	if num_cols:
		st.subheader('Distribuciones numéricas')
		col_num = st.selectbox('Elige columna numérica', num_cols)
		fig, ax = plt.subplots()
		sns.histplot(df[col_num].dropna(), kde=True, ax=ax)
		ax.set_xlabel(col_num)
		st.pyplot(fig)

		if len(num_cols) > 1:
			st.subheader('Correlación entre variables numéricas')
			fig2, ax2 = plt.subplots(figsize=(6, 4))
			sns.heatmap(df[num_cols].corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax2)
			st.pyplot(fig2)

	cat_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
	if cat_cols:
		st.subheader('Conteos por categoría')
		col_cat = st.selectbox('Elige columna categórica', cat_cols)
		top = df[col_cat].value_counts().head(15)
		fig3, ax3 = plt.subplots()
		sns.barplot(x=top.values, y=top.index, ax=ax3)
		st.pyplot(fig3)

	if dataset == 'Transacciones':
		st.subheader('Series temporales: Ventas agregadas por mes')
		df_time = transacciones.copy()
		df_time['Fecha_Venta'] = pd.to_datetime(df_time['Fecha_Venta'], errors='coerce')
		sales = df_time.groupby(df_time['Fecha_Venta'].dt.to_period('M'))['Precio_Venta_Final'].sum().dropna()
		if not sales.empty:
			sales.index = sales.index.to_timestamp()
			fig4, ax4 = plt.subplots()
			sales.plot(ax=ax4)
			ax4.set_ylabel('Total Precio_Venta_Final')
			st.pyplot(fig4)


if __name__ == '__main__':
	main()