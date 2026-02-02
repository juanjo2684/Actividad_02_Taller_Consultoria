# TechLogistics S.A.S – Decisión Ética en Curaduría de Datos

## Resumen Ejecutivo

El procesamiento aplicado sigue el principio: **"Preservar información cuando sea defendible; eliminar solo cuando sea comprometedor."**

---

## 1. FEEDBACK (Clientes)

### 1.1 Qué se ELIMINÓ (Duplicados Exactos)
**Decisión:** Eliminar registros duplicados 100%.

**Justificación:**
- Un feedback duplicado es una **redundancia pura** sin valor analítico.
- Causa: errores de ingreso o sincronización de sistemas.
- **Impacto:** Nulo en fidelidad; al contrario, reduce ruido.
- **Ejemplo:** Si dos registros idénticos (mismo cliente, feedback, fecha) existen, uno es error administrativo.

**Acción:** Drop duplicates (todas las columnas iguales).

---

### 1.2 Qué se IMPUTÓ (Edades fuera de rango)

**Registros identificados:** Edades < 18 o > 90 años (ej: 195 años).

**Decisión:** **IMPUTAR con MEDIANA** (no media).

---

### 1.3 Qué se IMPUTÓ (Recomendación de Marca)

**Registros identificados:** NaN, "N/A", valores inconsistentes.

**Decisión:** **IMPUTAR con MODA** (valor más frecuente).

---

## 2. INVENTARIO (Maestro de Productos)

### 2.1 Qué se ELIMINÓ

**Nada se eliminó por completo.**

---

### 2.2 Qué se IMPUTÓ

#### **2.2.1 Lead_Time_Dias**

**Registros identificados:** NaN, "nan", "Inmediato", "25-30 días" (texto sucio).

**Decisión:** **IMPUTAR con MEDIANA por Categoría**.

**Jerarquía:**
1. Primero: Imputar por **categoría** (mismo tipo de producto → tiempo similar).
2. Si categoría aún tiene NaN: Usar mediana **global**.

---

#### **2.2.2 Costo_Unitario_USD**

**Registros identificados:** Outliers detectados por **método IQR (Interquartile Range)**.

**Decisión:** **REEMPLAZAR OUTLIERS CON MEDIANA POR CATEGORÍA**.

---

#### **2.2.3 Stock_Actual**

**Registros identificados:** Valores negativos (ej: -5, -49 unidades).

**Decisión:** **CONVERTIR A POSITIVOS (valor absoluto)**.

**Justificación:**
- Stock negativo es **lógicamente imposible** en inventario real.
- Causa probable: Error de registro (devolución no reconciliada).
- **No es outlier a eliminar**, es error que debe corregirse.
- Tomar valor absoluto preserva la **magnitud del problema** (hay desajuste de 49 unidades).

---

## 3. TRANSACCIONES (Ventas)

### 3.1 Qué se ELIMINÓ

**Nada.** (Las transacciones son hechos históricos; eliminarlas oculta problemas.)

---

### 3.2 Qué se IMPUTÓ

#### **3.2.1 Cantidad_Vendida (valores negativos)**

**Registros identificados:** Cantidad < 0 (ej: -5 unidades).

**Decisión:** **CONVERTIR A POSITIVOS (valor absoluto)**.

**Justificación:**
- Cantidad negativa representa **devoluciones o ajustes**.
- No es error a eliminar; es transacción real que debe registrarse.
- Tomar absoluto preserva magnitud; el signo se captura en `Estado_Envio = Devuelto`.

---

#### **3.2.2 Tiempo_Entrega_Real (NaN)**

**Registros identificados:** Falta tiempo de entrega para ~12% de transacciones.

**Decisión:** **IMPUTAR CON MEDIANA por ruta (Bodega_Origen + Ciudad_Destino)**.

---

#### **3.2.3 Costo_Envio (NaN)**

**Registros identificados:** Falta costo para ~8% de transacciones.

**Decisión:** 
1. **Primero:** Si `Canal_Venta = Físico` → `Costo_Envio = 0` (sin envío).
2. **Luego:** Imputar restantes con **MEDIANA por ruta**.

**Justificación:**
- Venta física no requiere envío (costo lógicamente nulo).
- Para online: Mediana por ruta captura variabilidad logística.

---

## 4. SÍNTESIS DE DECISIÓN ÉTICA

| Dataset | Acción | Método | Justificación |
|---------|--------|--------|---------------|
| Feedback | Eliminar duplicados | Drop | Redundancia pura sin valor |
| Feedback | Imputar edades | Mediana | Robusta a outliers (195 años) |
| Feedback | Imputar marca | Moda | Variable categórica; refleja sentimiento |
| Inventario | Reemplazar costos outliers | Mediana/Categoría | Preserva fila; corrige error probable |
| Inventario | Imputar lead time | Mediana/Categoría | Contexto de negocio por tipo producto |
| Inventario | Corregir stock negativo | Abs() | Preserva magnitud; es desajuste real |
| Transacciones | Corregir cantidad negativa | Abs() | Es devolución, capturada en Estado |
| Transacciones | Imputar tiempo entrega | Mediana/Ruta | Contexto geográfico-logístico |
| Transacciones | Imputar costo envío | 0 o Mediana/Ruta | Lógica de canal + contexto |

---

## 5. PRINCIPIOS SUBYACENTES

1. **Máxima Preservación:** Nunca eliminar filas completas si el error es corregible.
2. **Contexto Operativo:** Usar mediana/moda respetando estructura de negocio (rutas, categorías).
3. **Robustez Estadística:** Mediana > Media cuando hay outliers; Moda para categóricas.
4. **Auditabilidad:** Toda decisión debe justificarse en términos de negocio + estadística.
5. **Señal vs. Ruido:** Valores imposibles (195 años) son ruido; devoluciones son señal.

---

