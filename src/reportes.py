# -*- coding: utf-8 -*-
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_reporte_ejecutivo_pdf(df_filtrado, health_scores, metricas_calidad):
    """
    Genera un reporte ejecutivo profesional en PDF con los hallazgos clave.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Estilos Personalizados
    style_title = ParagraphStyle('Title', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#1f4e78'), spaceAfter=20)
    style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#2e75b6'), spaceBefore=15, spaceAfter=10)
    style_normal = styles['Normal']

    # 1. Encabezado
    story.append(Paragraph("Reporte Ejecutivo de Auditoría TechLogistics", style_title))
    story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}", style_normal))
    story.append(Spacer(1, 12))

    # 2. Resumen de Salud del Dato (El valor de la limpieza)
    story.append(Paragraph("1. Calidad de la Información (Health Score)", style_h2))
    data_health = [["Dataset", "Score Inicial", "Score Post-Limpieza", "Mejora"]]
    
    for ds, scores in health_scores.items():
        mejora = scores['Despues'] - scores['Antes']
        data_health.append([ds, f"{scores['Antes']:.1f}%", f"{scores['Despues']:.1f}%", f"+{mejora:.1f}%"])

    t_health = Table(data_health, colWidths=[1.5*72, 1.2*72, 1.2*72, 1*72])
    t_health.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_health)
    story.append(Spacer(1, 15))

    # 3. Hallazgos Financieros (Preguntas 1 y 3)
    story.append(Paragraph("2. Resumen de Impacto Financiero", style_h2))
    
    ingreso_total = df_filtrado["ingreso_total"].sum()
    margen_total = df_filtrado["margen_real"].sum()
    ingreso_riesgo = df_filtrado[df_filtrado["venta_sin_inventario"]]["ingreso_total"].sum()
    
    data_fin = [
        ["Métrica de Negocio", "Valor Actual"],
        ["Ingresos Totales Analizados", f"USD ${ingreso_total:,.2f}"],
        ["Margen Neto Real (Post-Logística)", f"USD ${margen_total:,.2f}"],
        ["Ingreso en Riesgo (Venta Invisible)", f"USD ${ingreso_riesgo:,.2f}"],
        ["Rentabilidad sobre Ingresos", f"{(margen_total/ingreso_total*100):.2f}%" if ingreso_total > 0 else "0%"]
    ]
    
    t_fin = Table(data_fin, colWidths=[3*72, 2*72])
    t_fin.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (1, 2), (1, 2), colors.lightcoral if ingreso_riesgo > (ingreso_total*0.05) else colors.white)
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 15))

    # 4. Diagnóstico Operativo (Preguntas 2, 4 y 5)
    story.append(Paragraph("3. Diagnóstico de Riesgos Operativos", style_h2))
    
    nps_avg = df_filtrado["NPS_Numerico"].mean()
    casos_paradoja = df_filtrado["paradoja_fidelidad"].sum()
    
    resumen_ops = f"""Se ha detectado un NPS promedio de <b>{nps_avg:.2f}/10</b>. 
    Actualmente existen <b>{casos_paradoja} registros</b> que presentan la 'Paradoja de Fidelidad' 
    (Stock alto con satisfacción baja), lo cual sugiere ineficiencias en la estrategia de precios o calidad del producto."""
    
    story.append(Paragraph(resumen_ops, style_normal))

    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def obtener_reporte_csv(df_filtrado, tipo="general"):
    """Genera versiones CSV para descarga de datos crudos"""
    if tipo == "fuga":
        return df_filtrado[df_filtrado["margen_real"] < 0].to_csv(index=False).encode('utf-8')
    elif tipo == "invisible":
        return df_filtrado[df_filtrado["venta_sin_inventario"]].to_csv(index=False).encode('utf-8')
    return df_filtrado.to_csv(index=False).encode('utf-8')