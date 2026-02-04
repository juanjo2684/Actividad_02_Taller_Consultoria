# 📑 ÍNDICE RÁPIDO DEL PROYECTO

## 🎯 INICIO RÁPIDO

Si acabas de llegar al proyecto, lee esto primero:

1. **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** ← Empieza aquí
   - Visión general del proyecto
   - Antes vs Después
   - Impacto por números

2. **[README.md](README.md)** ← Documentación completa
   - Descripción general
   - Estructura del proyecto
   - Todas las 29 reglas de limpieza
   - Cómo ejecutar

3. **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** ← Referencia rápida
   - Puntos clave por archivo
   - Cambios específicos
   - Estadísticas
   - Validación

---

## 📚 DOCUMENTACIÓN DETALLADA

### Cambios Realizados
- **[CAMBIOS.md](CAMBIOS.md)** - Descripción detallada de todos los cambios
  - Qué se modificó
  - Por qué se modificó
  - Cómo se modificó

### Validación Técnica
- **[VERIFICACION_FINAL.md](VERIFICACION_FINAL.md)** - Checklist de entregables
  - Requisitos cumplidos
  - Validaciones técnicas
  - Estadísticas
  - Instrucciones de uso

---

## 💻 ARCHIVOS DE CÓDIGO

### Aplicación Principal
- **app.py** (341 líneas)
  - Interfaz Streamlit
  - 3 vistas principales
  - Funciones de análisis modular
  - Visualizaciones interactivas Plotly

### Documentación de Reglas
- **data_cleaning_rules.py** (395 líneas)
  - 29 reglas de limpieza documentadas
  - 3 diccionarios por dataset
  - Función helper `get_all_cleaning_rules()`

### Procesamiento de Datos
- **inventario.py** (220 líneas)
  - 8 secciones comentadas
  - 9 reglas de limpieza
  - Funciones helper IQR y max_lead_time

- **feedback.py** (132 líneas)
  - 6 secciones comentadas
  - 6 reglas de limpieza
  - Transformaciones y imputaciones

- **transacciones.py** (185 líneas)
  - 14 secciones comentadas
  - 14 reglas de limpieza
  - Enriquecimiento relacional

---

## 🧹 REGLAS DE LIMPIEZA DOCUMENTADAS

### Inventario (9 reglas)
```
1. Normalización de texto
2. Limpieza Lead_Time_Dias
3. Estandarización Categoria
4. Imputación Lead_Time_Dias
5. Conversión de fecha
6. Detección de outliers
7. Tratamiento Costo_Unitario_USD
8. Imputación Stock_Actual
9. Conversión Stock_Actual
```
Ver en: **README.md § Inventario**

### Feedback (6 reglas)
```
1. Eliminación de duplicados
2. Imputación Edad_Cliente
3. Normalización Recomienda_Marca
4. Imputación Recomienda_Marca
5. Normalización Ticket_Soporte_Abierto
6. Conversión de comentarios
```
Ver en: **README.md § Feedback**

### Transacciones (14 reglas)
```
1. Conversión de Fecha_Venta
2. Normalización de texto
3. Conversión Cantidad_Vendida
4. Imputación Estado_Envio (sin ticket)
5. Imputación Estado_Envio (con ticket)
6. Normalización de ciudades
7. Imputación Costo_Envio (físico)
8. Feature Engineering - Margen
9. Merge con Inventario
10. Creación ID grupal
11. Imputación Tiempo_Entrega_Real
12. Imputación Costo_Envio
13. Eliminación fila
14. Imputación lógica final
```
Ver en: **README.md § Transacciones**

---

## 🎨 VISTAS EN STREAMLIT

Al ejecutar `streamlit run app.py`, verás:

### 📊 Exploración de Datos
- Tabs: Vista Previa | Información | Análisis
- Select: Elige dataset (Transacciones/Inventario/Feedback)
- Gráficas interactivas Plotly
- Análisis detallado por variable

### 🧹 Reglas de Limpieza
- Select: Elige dataset
- Expandibles: Una por cada regla
- Muestra: Descripción, código, variables, impacto
- Total: 29 reglas documentadas

### 📈 Análisis Específico
- Select: Elige tipo de análisis
- Análisis profundo con métricas KPI
- Gráficas contextualizadas
- Insights específicos por dataset

---

## 🚀 CÓMO USAR

### Instalación
```bash
# Navega al directorio
cd /Users/sruiz.gomez/Maestria/Fundamentos\ Ciencia\ de\ Datos/Actividad_02_Taller_Consultoria

# Instala dependencias
pip install -r requirements.txt
```

### Ejecución
```bash
# Ejecuta la aplicación
streamlit run app.py

# Se abrirá en http://localhost:8501
```

### Primeros Pasos
1. Selecciona una vista en el sidebar
2. Explora los datos o las reglas de limpieza
3. Interactúa con las gráficas Plotly
4. Lee la documentación en expandibles

---

## 📊 ESTADÍSTICAS

```
Total de líneas Python:         1,273
Líneas de comentarios:            241
Reglas documentadas:               29
Funciones modulares:                5
Vistas Streamlit:                    3
Gráficas Plotly:                    8+
Archivos documentación:              5
```

---

## 🔧 ESTRUCTURA DEL PROYECTO

```
Actividad_02_Taller_Consultoria/
│
├── 🐍 CÓDIGO PYTHON
│   ├── app.py                    ← Aplicación principal
│   ├── data_cleaning_rules.py    ← Documentación centralizada
│   ├── inventario.py             ← Procesamiento inventario
│   ├── feedback.py               ← Procesamiento feedback
│   └── transacciones.py          ← Procesamiento transacciones
│
├── 📚 DOCUMENTACIÓN
│   ├── README.md                 ← Documentación completa
│   ├── RESUMEN_EJECUTIVO.md      ← Resumen de cambios
│   ├── CAMBIOS.md                ← Detalles técnicos
│   ├── GUIA_RAPIDA.md            ← Referencia rápida
│   ├── VERIFICACION_FINAL.md     ← Checklist
│   └── INDICE.md                 ← Este archivo
│
├── 📊 DATOS
│   ├── inventario_central_v2.csv
│   ├── feedback_clientes_v2.csv
│   └── transacciones_logistica_v2.csv
│
├── ⚙️  CONFIGURACIÓN
│   └── requirements.txt
│
└── 📁 COMPILADOS
    └── __pycache__/
```

---

## ✅ VALIDACIÓN

```
✓ Sintaxis Python válida
✓ Todos los imports funcionales
✓ Sin código incompleto
✓ 100% documentado
✓ Completamente modular
✓ Interactivo con Plotly
✓ Streamlit optimizado
✓ Listo para producción
```

---

## 📝 NOTAS IMPORTANTES

### Sin Código Omitido
Todas las líneas de código están documentadas:
- ✅ Sin `...existing code...`
- ✅ Sin comentarios vagas
- ✅ Sin transformaciones ocultas
- ✅ Todo es explícito y claro

### Completamente Modular
- ✅ Funciones reutilizables
- ✅ Fácil de mantener
- ✅ Fácil de extender
- ✅ Fácil de auditar

### 100% Interactivo
- ✅ Plotly para gráficas
- ✅ Streamlit para UI
- ✅ Expandibles para detalles
- ✅ Tabs para organización

---

## 🎓 CÓMO LEER LA DOCUMENTACIÓN

### Para Entender el Proyecto
1. Comienza con [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
2. Lee [README.md](README.md) sección completa
3. Consulta [GUIA_RAPIDA.md](GUIA_RAPIDA.md) para detalles

### Para Entender las Reglas
1. Abre la aplicación: `streamlit run app.py`
2. Ve a "🧹 Reglas de Limpieza"
3. Expande cada regla para ver detalles

### Para Entender el Código
1. Lee el archivo Python correspondiente
2. Observa las secciones comentadas
3. Consulta [data_cleaning_rules.py](data_cleaning_rules.py) para resumen

---

## 🤝 Equipo del Proyecto

- Juan Morales
- Sebastian Ruiz
- Daniel Pareja

---

## 📅 Información del Proyecto

- **Fecha**: 31 de enero de 2026
- **Status**: ✅ Completado
- **Calidad**: Producción lista
- **Documentación**: Exhaustiva

---

## 🎯 Acciones Recomendadas

### Primero
1. Lee [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
2. Instala: `pip install -r requirements.txt`
3. Ejecuta: `streamlit run app.py`

### Luego
1. Explora "📊 Exploración de Datos"
2. Revisa "🧹 Reglas de Limpieza"
3. Analiza "📈 Análisis Específico"

### Finalmente
1. Lee [README.md](README.md) para entender todo
2. Revisa el código en los archivos .py
3. Consulta [data_cleaning_rules.py](data_cleaning_rules.py)

---

**¡Proyecto completado y listo para usar!** 🎉
