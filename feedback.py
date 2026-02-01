import numpy as np
import pandas as pd


def clean_feedback_dataset(file_path):
    """
    Limpieza integral y auditada del dataset de feedback de clientes.
    
    Pasos de limpieza:
    1. Eliminación de duplicados exactos
    2. Imputación de Edad_Cliente (fuera de rango 18-90)
    3. Normalización de Recomienda_Marca (binaria: SI/NO)
    4. Normalización de Ticket_Soporte_Abierto (booleana)
    5. Conversión de comentarios a string
    
    Parámetros:
    -----------
    file_path : str
        Ruta del archivo CSV
    
    Retorna:
    --------
    pd.DataFrame : Feedback limpio
    """

    # Cargar CSV
    df_raw = pd.read_csv(file_path)

    # Realizar copia para no modificar original
    df = df_raw.copy()

    # ==========================================
    # AUDITORÍA INICIAL
    # ==========================================
    # Calcular porcentaje de nulos antes de limpieza
    null_report_before = (
        df.isna()
        .mean()
        .mul(100)
        .round(2)
        .reset_index()
        .rename(columns={"index": "Columna", 0: "Porcentaje_Nulos"})
    )

    # Contar duplicados exactos
    n_duplicates_before = df.duplicated().sum()

    # Resumen de salud del dataset
    health_before = {
        "registros_totales": df.shape[0],
        "duplicados_detectados": n_duplicates_before,
        "nulidad_promedio_%": round(null_report_before["Porcentaje_Nulos"].mean(), 2),
    }

    # ==========================================
    # PASO 1: ELIMINACIÓN DE DUPLICADOS EXACTOS
    # ==========================================
    # Remover filas completamente duplicadas
    df = df.drop_duplicates()
    # Nota: Se pierden n_duplicates_before filas

    # ==========================================
    # PASO 2: IMPUTACIÓN DE EDAD_CLIENTE
    # ==========================================
    # Seleccionar edades válidas (18-90 años)
    edad_mediana = df.loc[
        df["Edad_Cliente"].between(18, 90), 
        "Edad_Cliente"
    ].median()

    # Reemplazar edades fuera de rango con la mediana
    df.loc[
        ~df["Edad_Cliente"].between(18, 90), 
        "Edad_Cliente"
    ] = edad_mediana
    # Nota: Esto trata valores <18, >90 y también NaN

    # ==========================================
    # PASO 3: NORMALIZACIÓN DE RECOMIENDA_MARCA
    # ==========================================
    # Operaciones secuenciales:
    # 1. Convertir a string
    # 2. Eliminar espacios
    # 3. Convertir a mayúsculas
    # 4. Mapear variantes inconsistentes
    df["Recomienda_Marca"] = (
        df["Recomienda_Marca"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace({"0": "NO", "SÍ": "SI"})  # Mapeo: "SÍ" -> "SI", "0" -> "NO"
    )

    # Calcular moda (valor más frecuente)
    moda_recomienda = df["Recomienda_Marca"].mode()[0]
    
    # Llenar valores nulos con la moda
    df["Recomienda_Marca"] = df["Recomienda_Marca"].fillna(moda_recomienda)
    # Nota: Se imputan nulos con el valor más frecuente

    # ==========================================
    # PASO 4: NORMALIZACIÓN Y CONVERSIÓN A BOOLEANO
    # ==========================================
    # Operaciones secuenciales para Ticket_Soporte_Abierto:
    # 1. Convertir a string
    # 2. Eliminar espacios
    # 3. Convertir a mayúsculas
    # 4. Mapear "SÍ" a "SI" (normalización)
    df["Ticket_Soporte_Abierto"] = (
        df["Ticket_Soporte_Abierto"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace({"SÍ": "SI", "0": "NO"})  # Mapeo de variantes
    )

    # Mapear a booleano
    df["Ticket_Soporte_Abierto"] = df["Ticket_Soporte_Abierto"].map(
        {"SI": True, "NO": False}  # SI -> True, NO -> False
    )
    # Nota: Resultado es True/False

    # ==========================================
    # PASO 5: ASEGURAR TIPO STRING DE COMENTARIOS
    # ==========================================
    # Convertir comentarios a string (prevenir errores en procesamiento posterior)
    df["Comentario_Texto"] = df["Comentario_Texto"].astype("string")

    # ==========================================
    # RESULTADO FINAL
    # ==========================================
    # Retornar dataset limpio

    return df
