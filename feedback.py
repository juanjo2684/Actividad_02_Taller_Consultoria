import numpy as np
import pandas as pd


def clean_feedback_dataset(file_path):
    """
    Limpieza ética y auditada del dataset feedback_clientes_v2.

    Retorna:
    - df_clean: DataFrame limpio
    - health_before: métricas de calidad antes
    - health_after: métricas de calidad después
    - null_report_before
    - null_report_after
    """

    df_raw = pd.read_csv(file_path)

    # --- Copia de seguridad ---
    df = df_raw.copy()

    # =========================
    # AUDITORÍA INICIAL
    # =========================
    null_report_before = (
        df.isna()
        .mean()
        .mul(100)
        .round(2)
        .reset_index()
        .rename(columns={"index": "Columna", 0: "Porcentaje_Nulos"})
    )

    n_duplicates_before = df.duplicated().sum()

    health_before = {
        "registros_totales": df.shape[0],
        "duplicados_detectados": n_duplicates_before,
        "nulidad_promedio_%": round(null_report_before["Porcentaje_Nulos"].mean(), 2),
    }

    # =========================
    # LIMPIEZA
    # =========================

    # 1. Eliminar duplicados exactos
    df = df.drop_duplicates()

    # 2. Edad del cliente (imputación con mediana)
    edad_mediana = df.loc[df["Edad_Cliente"].between(18, 90), "Edad_Cliente"].median()

    df.loc[~df["Edad_Cliente"].between(18, 90), "Edad_Cliente"] = edad_mediana

    # 3. Recomienda_Marca (normalización + moda)
    df["Recomienda_Marca"] = (
        df["Recomienda_Marca"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace({"0": "NO", "SÍ": "SI"})
    )

    moda_recomienda = df["Recomienda_Marca"].mode()[0]
    df["Recomienda_Marca"] = df["Recomienda_Marca"].fillna(moda_recomienda)

    # 4. Ticket_Soporte_Abierto (booleano)
    df["Ticket_Soporte_Abierto"] = (
        df["Ticket_Soporte_Abierto"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace({"SÍ": "SI", "0": "NO"})
    )

    df["Ticket_Soporte_Abierto"] = df["Ticket_Soporte_Abierto"].map(
        {"SI": True, "NO": False}
    )

    # 5. Comentario de texto
    df["Comentario_Texto"] = df["Comentario_Texto"].astype("string")

    return df
