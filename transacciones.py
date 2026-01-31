import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def procesar_transacciones(ruta_transacciones,df_inventario,df_feedback):

    path = ruta_transacciones
    df_transacciones = pd.read_csv(path)

    df_transacciones.info()

    df_transacciones['Fecha_Venta'] = pd.to_datetime(df_transacciones['Fecha_Venta'])
    df_transacciones.info()

    #Todo a minusculas

    cols_texto = df_transacciones.select_dtypes(include=['object', 'string']).columns
    df_transacciones[cols_texto] = df_transacciones[cols_texto].apply(lambda x: x.str.lower())

    #Rellenar estado df_feedback == archivo juan jose

    transacciones_nps_no = df_feedback[df_feedback['Ticket_Soporte_Abierto'] == 'no']
    transacciones_nps_no = df_feedback['Transaccion_ID'].unique()

    condicion_existe = df_transacciones['Transaccion_ID'].isin(transacciones_nps_no)
    condicion_vacio = df_transacciones['Estado_Envio'].isna()

    df_transacciones.loc[condicion_existe & condicion_vacio, 'Estado_Envio'] = 'entregado'

    transacciones_nps_si = df_feedback[df_feedback['Ticket_Soporte_Abierto'] == 'sí']
    transacciones_nps_si = df_feedback['Transaccion_ID'].unique()

    condicion_existe = df_transacciones['Transaccion_ID'].isin(transacciones_nps_si)
    condicion_vacio = df_transacciones['Estado_Envio'].isna()

    df_transacciones.loc[condicion_existe & condicion_vacio, 'Estado_Envio'] = 'devuelto'

    #Limpieza ciudades

    dic_ciudades = {'bog': 'bogotá', 'med': 'medellín'}
    df_transacciones.replace(dic_ciudades, inplace= True)
    df_transacciones['Ciudad_Destino'].value_counts()

    #relleno costo encio

    df_transacciones.loc[df_transacciones['Canal_Venta'] == 'físico', 'Costo_Envio'] = 0

    #Margenes

    df_transacciones['margen'] = df_transacciones['Precio_Venta_Final'] - df_transacciones['Costo_Envio']
    df_transacciones['margen %'] = df_transacciones['margen'] / df_transacciones['Precio_Venta_Final']
    df_transacciones[['margen', 'margen %']]

    # Sobreescribimos df_transacciones agregándole la columna Bodega df_stock = archivo sebas

    df_transacciones = df_transacciones.merge(
        df_inventario[['SKU_ID', 'Bodega_Origen']],  # Truco: Seleccionamos solo 'id' y 'bodega' para no traer basura extra
        on='SKU_ID',                  # La llave común
        how='left'                # 'left' asegura que NO pierdas filas de df_transacciones si no hay match
    )

    #Id para las medias

    df_transacciones['id_tiempos_entrega'] = df_transacciones['Bodega_Origen'] + "-" + df_transacciones['Ciudad_Destino']

    # Rellenar NaNs con la mediana específica de su grupo (id_tiempos_entrega)
    df_transacciones['Tiempo_Entrega_Real'] = df_transacciones['Tiempo_Entrega_Real'].fillna(
        df_transacciones.groupby('id_tiempos_entrega')['Tiempo_Entrega_Real'].transform('median')
    )

    # Rellenar NaNs con la mediana específica de su grupo (id_tiempos_entrega)
    df_transacciones['Costo_Envio'] = df_transacciones['Costo_Envio'].fillna(
        df_transacciones.groupby('id_tiempos_entrega')['Costo_Envio'].transform('median')
    )

    df_transacciones.drop(0, inplace=True)

    fecha_max = df_transacciones.Fecha_Venta.max()

    df_transacciones['Fecha_Calculada'] = df_transacciones.apply(lambda x: x['Fecha_Venta'] + pd.DateOffset(day=x['Tiempo_Entrega_Real']), axis=1)

    df_transacciones.loc[lambda x: (x['Fecha_Calculada'] < fecha_max) & (x['Estado_Envio'].isna()), 'Estado_Envio'] = 'ent.regado'
    df_transacciones.loc[lambda x: (x['Fecha_Calculada'] >= fecha_max) & (x['Estado_Envio'].isna()), 'Estado_Envio'] = 'en camino'

    return df_transacciones
