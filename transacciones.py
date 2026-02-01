import pandas as pd
import numpy as np


def procesar_transacciones(ruta_transacciones, df_inventario, df_feedback):
    """
    Procesamiento completo de datos de transacciones incluyendo:
    - Conversión de tipos
    - Normalización de texto
    - Imputación condicional usando datos relacionales
    - Cálculo de métricas
    - Enriquecimiento con datos de inventario y feedback
    
    Parámetros:
    -----------
    ruta_transacciones : str
        Ruta del archivo CSV de transacciones
    df_inventario : pd.DataFrame
        DataFrame de inventario (procesado)
    df_feedback : pd.DataFrame
        DataFrame de feedback (procesado)
    
    Retorna:
    --------
    pd.DataFrame : Transacciones procesadas y enriquecidas
    """

    path = ruta_transacciones
    df_transacciones = pd.read_csv(path)

    # ==========================================
    # PASO 1: CONVERSIÓN DE TIPOS DE DATO
    # ==========================================
    # Convertir Fecha_Venta a datetime para análisis temporal
    df_transacciones['Fecha_Venta'] = pd.to_datetime(df_transacciones['Fecha_Venta'])

    # ==========================================
    # PASO 2: NORMALIZACIÓN DE TEXTO
    # ==========================================
    # Convertir todas las columnas de texto a minúsculas
    # Esto facilita comparaciones y evita inconsistencias
    cols_texto = df_transacciones.select_dtypes(include=['object', 'string']).columns
    df_transacciones[cols_texto] = df_transacciones[cols_texto].apply(lambda x: x.str.lower())
    
    # ==========================================
    # PASO 3: CONVERSIÓN DE CANTIDAD_VENDIDA A POSITIVO
    # ==========================================
    # Valores negativos son errores de entrada, se convierten a positivos
    df_transacciones.loc[:, 'Cantidad_Vendida'] = df_transacciones.loc[:, 'Cantidad_Vendida'].abs()
    
    # ==========================================
    # PASO 4: IMPUTACIÓN CONDICIONAL DE ESTADO_ENVIO
    # ==========================================
    # Estrategia: Usar información de feedback para inferir estado de envío
    
    # Paso 4a: Transacciones SIN ticket de soporte -> "entregado"
    # (clientes sin problemas, no abrieron ticket)
    transacciones_nps_no = df_feedback['Transaccion_ID'].unique()
    
    condicion_existe = df_transacciones['Transaccion_ID'].isin(transacciones_nps_no)
    condicion_vacio = df_transacciones['Estado_Envio'].isna()
    
    df_transacciones.loc[condicion_existe & condicion_vacio, 'Estado_Envio'] = 'entregado'

    # Paso 4b: Transacciones CON ticket de soporte abierto -> "devuelto"
    # (clientes con problemas, abrieron ticket)
    transacciones_nps_si = df_feedback['Transaccion_ID'].unique()
    
    condicion_existe = df_transacciones['Transaccion_ID'].isin(transacciones_nps_si)
    condicion_vacio = df_transacciones['Estado_Envio'].isna()
    
    df_transacciones.loc[condicion_existe & condicion_vacio, 'Estado_Envio'] = 'devuelto'

    # ==========================================
    # PASO 5: NORMALIZACIÓN DE CIUDADES DESTINO
    # ==========================================
    # Mapeo de abreviaturas a nombres completos
    dic_ciudades = {
        'bog': 'bogotá',      # Bogotá
        'med': 'medellín'     # Medellín
    }
    df_transacciones.replace(dic_ciudades, inplace=True)

    # ==========================================
    # PASO 6: IMPUTACIÓN SELECTIVA DE COSTO_ENVIO
    # ==========================================
    # Lógica de negocio: No hay envío en transacciones de canal físico (tienda)
    df_transacciones.loc[
        df_transacciones['Canal_Venta'] == 'físico', 
        'Costo_Envio'
    ] = 0

    # ==========================================
    # PASO 7: FEATURE ENGINEERING - MÁRGENES
    # ==========================================
    # Crear métricas de rentabilidad
    
    # Margen absoluto: Precio_Venta_Final - Costo_Envio
    df_transacciones['margen'] = (
        df_transacciones['Precio_Venta_Final'] - df_transacciones['Costo_Envio']
    )
    
    # Margen porcentual: (Margen / Precio_Venta_Final) * 100
    df_transacciones['margen %'] = (
        df_transacciones['margen'] / df_transacciones['Precio_Venta_Final']
    )

    # ==========================================
    # PASO 8: ENRIQUECIMIENTO - MERGE CON INVENTARIO
    # ==========================================
    # Traer información de bodega del inventario
    # Left join: Mantener todas las transacciones, agregar bodega si existe
    df_transacciones = df_transacciones.merge(
        df_inventario[['SKU_ID', 'Bodega_Origen']],  # Solo columnas necesarias
        on='SKU_ID',                                   # Llave de unión
        how='left'                                     # Left join
    )

    # ==========================================
    # PASO 9: CREACIÓN DE IDENTIFICADOR GRUPAL
    # ==========================================
    # Crear ID único para cada ruta bodega-ciudad
    # Útil para imputación de tiempos y costos por ruta
    df_transacciones['id_tiempos_entrega'] = (
        df_transacciones['Bodega_Origen'] + "-" + df_transacciones['Ciudad_Destino']
    )

    # ==========================================
    # PASO 10: IMPUTACIÓN GRUPAL - TIEMPO_ENTREGA_REAL
    # ==========================================
    # Llenar nulos con la mediana del grupo bodega-ciudad
    # Esto mantiene consistencia de tiempos por ruta
    df_transacciones['Tiempo_Entrega_Real'] = df_transacciones['Tiempo_Entrega_Real'].fillna(
        df_transacciones.groupby('id_tiempos_entrega')['Tiempo_Entrega_Real'].transform('median')
    )

    # ==========================================
    # PASO 11: IMPUTACIÓN GRUPAL - COSTO_ENVIO
    # ==========================================
    # Llenar nulos con la mediana del grupo bodega-ciudad
    # Mantiene costos realistas por ruta
    df_transacciones['Costo_Envio'] = df_transacciones['Costo_Envio'].fillna(
        df_transacciones.groupby('id_tiempos_entrega')['Costo_Envio'].transform('median')
    )

    # ==========================================
    # PASO 12: ELIMINACIÓN DE FILA PROBLEMÁTICA
    # ==========================================
    # Remover índice 0 (posible dato de prueba o erróneo)
    df_transacciones.drop(0, inplace=True)

    # ==========================================
    # PASO 13: CÁLCULO DE FECHA CALCULADA
    # ==========================================
    # Calcular fecha esperada de entrega
    # Formula: Fecha_Venta + Tiempo_Entrega_Real (en días)
    fecha_max = df_transacciones.Fecha_Venta.max()
    
    df_transacciones['Fecha_Calculada'] = df_transacciones.apply(
        lambda x: x['Fecha_Venta'] + pd.DateOffset(day=int(x['Tiempo_Entrega_Real'])), 
        axis=1
    )

    # ==========================================
    # PASO 14: IMPUTACIÓN LÓGICA FINAL - ESTADO_ENVIO
    # ==========================================
    # Paso 14a: Marcar como "ent.regado" (entregado)
    # Si la fecha calculada es menor a la fecha máxima del dataset
    # Significa que debería haber llegado ya
    df_transacciones.loc[
        (df_transacciones['Fecha_Calculada'] < fecha_max) & (df_transacciones['Estado_Envio'].isna()),
        'Estado_Envio'
    ] = 'ent.regado'
    
    # Paso 14b: Marcar como "en camino"
    # Si la fecha calculada es mayor a la fecha máxima
    # Significa que aún está en tránsito (no debería haber llegado)
    df_transacciones.loc[
        (df_transacciones['Fecha_Calculada'] >= fecha_max) & (df_transacciones['Estado_Envio'].isna()),
        'Estado_Envio'
    ] = 'en camino'

    # ==========================================
    # RESULTADO FINAL
    # ==========================================

    return df_transacciones.reset_index(drop=True)