# 📚 Ejemplos Prácticos del CLI Interactivo

## 🎯 Escenarios Reales de Uso

### 1. 📊 Analista de Datos - Exploración Rápida

**Situación:** Ana necesita explorar un archivo CSV de ventas para crear un dashboard.

**Comando:**

```bash
python cli_interactive.py
```

**Flujo recomendado:**

1. ✅ **Archivo**: `sales_data_2024.csv`
2. 🏷️ **Tabla**: `sales_2024`
3. 🚀 **Nivel**: Rápido (automático)
4. 🧪 **Filas**: Muestra pequeña (100 filas)

**Resultado:**

```sql
CREATE TABLE sales_2024 (
    id INT,
    date_ DATETIME,
    product_name VARCHAR(255),
    amount DECIMAL(10,2),
    customer_id INT
);

-- 100 INSERT statements
```

**Tiempo:** ~30 segundos

---

### 2. 🏢 Desarrollador Backend - Migración de Base de Datos

**Situación:** Carlos debe migrar datos de usuarios de un sistema legacy.

**Comando:**

```bash
python cli_interactive.py
```

**Flujo recomendado:**

1. ✅ **Archivo**: `legacy_users.csv`
2. 🏷️ **Tabla**: `users_migration`
3. 🔧 **Nivel**: Avanzado (nombres + tipos)
4. 📈 **Filas**: Muestra grande (50,000 filas)

**Personalizaciones realizadas:**

```
📋 Cambios de Columnas:
user_id → id (INT → BIGINT)
full_name → name (VARCHAR(50) → VARCHAR(100))
email_address → email (VARCHAR(50) → VARCHAR(255))
created_at → created_date (VARCHAR(50) → DATETIME)
```

**Resultado:**

```sql
CREATE TABLE users_migration (
    id BIGINT,
    name VARCHAR(100),
    email VARCHAR(255),
    created_date DATETIME,
    status ENUM('active','inactive','suspended')
);
```

**Tiempo:** ~5 minutos

---

### 3. 🔬 Data Scientist - Análisis Detallado

**Situación:** María necesita analizar un dataset de profiles para ML.

**Comando:**

```bash
python cli_interactive.py
```

**Flujo recomendado:**

1. ✅ **Archivo**: `profiles_dataset.csv`
2. 🏷️ **Tabla**: `ml_profiles_features`
3. 🎯 **Nivel**: Experto (control total)
4. 📊 **Filas**: Muestra mediana (5,000 filas)

**Análisis columna por columna:**

**Columna: age**

```
📊 Estadísticas Mostradas:
Mínimo: 18
Máximo: 89
Promedio: 34.5

🔧 Configuración Elegida:
Nombre: age_years
Tipo: INT (validado que no hay decimales)
```

**Columna: salary_range**

```
🔝 Valores Más Frecuentes:
"50,000-75,000" → 1,234 apariciones
"75,000-100,000" → 987 apariciones
"100,000-150,000" → 756 apariciones

🔧 Configuración Elegida:
Nombre: salary_bracket
Tipo: VARCHAR(50) (mantener formato texto)
```

**Tiempo:** ~15 minutos

---

### 4. 🚀 Startup - Importación de Datos de Clientes

**Situación:** El equipo de TechStart debe importar 100K registros de clientes.

**Comando:**

```bash
python cli_interactive.py
```

**Flujo de producción:**

1. ✅ **Archivo**: `customers_export.csv`
2. 🏷️ **Tabla**: `customers`
3. ⚙️ **Nivel**: Intermedio (revisar nombres)
4. 🌍 **Filas**: Archivo completo

**Revisión de nombres:**

```
📝 Cambios Realizados:
"Customer ID" → customer_id ✅
"First Name" → first_name ✅
"Last Name" → last_name ✅
"E-mail Address" → email ✏️ (personalizado)
"Phone Number" → phone ✏️ (personalizado)
"Registration Date" → registered_at ✏️ (personalizado)
```

**Progreso mostrado:**

```
⠦ Procesando datos... ████████████████████████████████████████ 100%

📊 Resultados:
- Filas procesadas: 100,000
- Tiempo total: 45 segundos
- Archivo SQL: 67 MB
- Velocidad: 2,222 filas/segundo
```

**Tiempo total:** ~8 minutos

---

## 🛠️ Casos Especiales y Soluciones

### 🔧 Problema: Columnas con Caracteres Especiales

**Archivo CSV:**

```csv
"Product-Name","Price ($)","Date/Time","Status?"
"Laptop Pro","1,299.99","2024-01-15 10:30","Active"
```

**Solución Automática:**

```
🔄 Limpieza Automática de Nombres:
"Product-Name" → product_name
"Price ($)" → price____
"Date/Time" → date_time
"Status?" → status_
```

**Configuración Mejorada (Nivel Intermedio):**

```
📝 Nombres Personalizados:
product_name ✅ (mantener)
price____ → price ✏️ (mejorar)
date_time ✅ (mantener)
status_ → is_active ✏️ (más descriptivo)
```

---

### 🔧 Problema: Tipos de Datos Mixtos

**Columna problemática:** `phone_number`

```
Ejemplos de datos:
"555-123-4567"
"(555) 123-4567"
"+1-555-123-4567"
"5551234567"
null
```

**Análisis Experto:**

```
📊 Información Detectada:
Tipo Pandas: object
Valores únicos: 8,543
Valores nulos: 127
Longitud máxima: 17 caracteres

💡 Tipo detectado: VARCHAR(50)

🔧 Configuración Recomendada:
Nombre: phone
Tipo: VARCHAR(20) ✏️ (optimizado)
```

---

### 🔧 Problema: Fechas en Múltiples Formatos

**Columna problemática:** `created_date`

```
Ejemplos detectados:
"2024-01-15"
"01/15/2024"
"January 15, 2024"
"2024-01-15 10:30:45"
```

**Decisión en Modo Avanzado:**

```
⚠️ Advertencia: Formatos de fecha inconsistentes detectados

🔧 Opciones Disponibles:
1. VARCHAR(50) - Mantener como texto ✅ (seguro)
2. DATETIME - Convertir (puede fallar)
3. TEXT - Para datos largos

✅ Selección: VARCHAR(50)
💡 Recomendación: Limpiar datos antes de importar
```

---

## 📈 Comparativa de Rendimiento

### 🧪 Muestra Pequeña (100 filas)

```
⏱️ Tiempo Promedio por Nivel:
🚀 Rápido:    15-30 segundos
⚙️ Intermedio: 1-2 minutos
🔧 Avanzado:   2-4 minutos
🎯 Experto:    5-8 minutos
```

### 📊 Muestra Mediana (5,000 filas)

```
⏱️ Tiempo Promedio por Nivel:
🚀 Rápido:    30-45 segundos
⚙️ Intermedio: 2-5 minutos
🔧 Avanzado:   5-10 minutos
🎯 Experto:    10-20 minutos
```

### 📈 Muestra Grande (50,000 filas)

```
⏱️ Tiempo Promedio por Nivel:
🚀 Rápido:    1-2 minutos
⚙️ Intermedio: 5-10 minutos
🔧 Avanzado:   10-20 minutos
🎯 Experto:    20-40 minutos
```

### 🌍 Archivo Completo (1M+ filas)

```
⏱️ Tiempo Estimado:
🚀 Rápido:    5-15 minutos
⚙️ Intermedio: 15-30 minutos
🔧 Avanzado:   30-60 minutos
🎯 Experto:    60-120 minutos

💡 Recomendación: Usar muestra primero
```

---

## 🎨 Personalización por Industria

### 🏥 Healthcare/Medicina

```sql
-- Tabla sugerida: patient_records
CREATE TABLE patient_records (
    patient_id BIGINT,
    medical_record_number VARCHAR(50),
    admission_date DATETIME,
    diagnosis_code VARCHAR(20),
    treatment_cost DECIMAL(12,2)
);
```

### 🛒 E-commerce

```sql
-- Tabla sugerida: product_catalog
CREATE TABLE product_catalog (
    sku VARCHAR(100),
    product_name VARCHAR(255),
    category_id INT,
    price DECIMAL(10,2),
    stock_quantity INT,
    is_active BOOLEAN
);
```

### 🏦 Finanzas

```sql
-- Tabla sugerida: transaction_history
CREATE TABLE transaction_history (
    transaction_id BIGINT,
    account_number VARCHAR(50),
    transaction_date DATETIME,
    amount DECIMAL(15,2),
    transaction_type ENUM('debit','credit'),
    description TEXT
);
```

### 📚 Educación

```sql
-- Tabla sugerida: student_grades
CREATE TABLE student_grades (
    student_id BIGINT,
    course_code VARCHAR(20),
    semester VARCHAR(20),
    grade DECIMAL(4,2),
    credits INT,
    grade_date DATE
);
```

---

## 🚨 Solución de Problemas Comunes

### ❌ Error: "Archivo muy grande"

```
💡 Solución:
1. Usar muestra primero (🧪 100 filas)
2. Validar configuración
3. Procesar archivo completo
4. Considerar dividir archivo
```

### ❌ Error: "Memoria insuficiente"

```
💡 Solución:
1. Cerrar otras aplicaciones
2. Usar chunks más pequeños (500 filas)
3. Procesar en lotes más pequeños
```

### ❌ Error: "Caracteres especiales"

```
💡 Solución:
1. Sistema los limpia automáticamente
2. Revisar en modo Intermedio
3. Personalizar nombres problemáticos
```

### ❌ Error: "Tipos incompatibles"

```
💡 Solución:
1. Usar modo Avanzado o Experto
2. Revisar datos con estadísticas
3. Elegir VARCHAR para datos mixtos
```

---

## 🏆 Mejores Prácticas Recomendadas

### ✅ Para Principiantes

1. **Empezar siempre con muestra pequeña**
2. **Usar modo Rápido primero**
3. **Revisar preview antes de procesar todo**
4. **Guardar configuración exitosa**

### ✅ Para Usuarios Avanzados

1. **Modo Experto para control total**
2. **Analizar estadísticas detalladas**
3. **Optimizar tipos de datos**
4. **Documentar decisiones de diseño**

### ✅ Para Producción

1. **Validar con muestra representativa**
2. **Usar nombres descriptivos**
3. **Considerar índices futuros**
4. **Planificar crecimiento de datos**

---

## 📝 Plantillas de Configuración

### 🔄 Configuración Estándar E-commerce

```
📋 Plantilla Recomendada:
Tabla: products
Columnas típicas:
- product_id → id (BIGINT)
- name → product_name (VARCHAR(255))
- price → price (DECIMAL(10,2))
- category → category (VARCHAR(100))
- stock → stock_quantity (INT)
- active → is_active (BOOLEAN)
```

### 🔄 Configuración Estándar CRM

```
📋 Plantilla Recomendada:
Tabla: contacts
Columnas típicas:
- contact_id → id (BIGINT)
- first_name → first_name (VARCHAR(100))
- last_name → last_name (VARCHAR(100))
- email → email (VARCHAR(255))
- phone → phone (VARCHAR(20))
- company → company_name (VARCHAR(255))
```

---

**🎯 ¡Ahora estás listo para convertir cualquier CSV como un profesional!**
