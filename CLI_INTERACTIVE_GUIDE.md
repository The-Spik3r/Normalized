# 🎮 Guía Completa del CLI Interactivo

## 🚀 Introducción

El **CLI Interactivo** es la nueva forma recomendada de usar el CSV to SQL Converter. Proporciona una experiencia visual hermosa, intuitiva y con control total sobre la conversión.

## ✨ Características Visuales

- 🎨 **Interfaz hermosa** con colores y emojis
- 📊 **Tablas formateadas** para mostrar datos
- 📈 **Barras de progreso animadas**
- 🎯 **Menús de navegación intuitivos**
- 📋 **Paneles informativos** con bordes estilizados
- ⚡ **Feedback en tiempo real**

---

## 🎬 Flujo Completo Paso a Paso

### 1. 🏁 Inicio del CLI

```bash
python cli_interactive.py
```

**Pantalla de Bienvenida:**

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    🚀 CSV TO SQL CONVERTER - INTERACTIVE CLI 🚀               ║
║                                                               ║
║    ✨ Convierte archivos CSV a SQL con personalización        ║
║    🎨 Interfaz interactiva con animaciones                    ║
║    ⚙️  Control total sobre nombres y tipos de datos           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

 📅 Fecha:     2025-11-07 10:30:15
 💻 Sistema:   CSV to SQL Interactive Converter v2.0
 🎯 Objetivo:  Conversión personalizada de CSV a SQL

¿Comenzamos la conversión interactiva? [y/n] (y):
```

### 2. 📁 Selección de Archivo CSV

**Detección Automática:**

```
📁 SELECCIÓN DE ARCHIVO CSV
──────────────────────────────────────────────────
📋 Archivos CSV encontrados:
  1. ../United-States-(Washington)-1,121,721.csv (353.3 MB)
  2. ./data/sales_data.csv (25.1 MB)
  3. ./exports/users.csv (5.8 MB)

[?] Selecciona el archivo CSV:
 > ../United-States-(Washington)-1,121,721.csv
   ./data/sales_data.csv
   ./exports/users.csv
   🔍 Especificar ruta manualmente
```

**Información del Archivo:**

```
✅ Archivo seleccionado: ../United-States-(Washington)-1,121,721.csv
📏 Tamaño: 353.25 MB
```

### 3. 🔍 Análisis de Estructura

**Análisis Automático con Animación:**

```
🔍 ANÁLISIS DE ESTRUCTURA
──────────────────────────────────────────────────
⠦ Analizando archivo CSV...
```

**Resultados del Análisis:**

```
      📊 Información del Archivo
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Propiedad        ┃ Valor           ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Columnas         │ 20              │
│ Filas analizadas │ 1,000 (muestra) │
│ Tipos únicos     │ 3               │
└──────────────────┴─────────────────┘

📋 Vista Previa de Datos:
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ pnum  ┃ location_locality  ┃ location_region      ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 1105  │ washington         │ district of columbia │
│ 1392  │ washington         │ district of columbia │
│ 1392  │ washington         │ district of columbia │
└───────┴────────────────────┴──────────────────────┘
... y 15 columnas más
```

### 4. 🏷️ Configuración de Tabla

**Nombre de Tabla:**

```
🏷️  CONFIGURACIÓN DE TABLA
──────────────────────────────────────────────────
💡 Nombre sugerido: united_states__washington__1_121_721

[?] ¿Qué deseas hacer con el nombre de la tabla?:
 > ✅ Usar nombre sugerido: united_states__washington__1_121_721
   ✏️  Especificar nombre personalizado
   🎲 Generar nombre aleatorio
```

**Si eliges personalizado:**

```
📝 Ingresa el nombre de la tabla: profiles
✅ Nombre de tabla configurado: profiles
```

### 5. 🏗️ Configuración de Columnas

**Selección de Nivel:**

```
🏗️  CONFIGURACIÓN DE COLUMNAS
──────────────────────────────────────────────────

[?] ¿Qué nivel de personalización deseas?:
 > 🚀 Rápido - Usar configuración automática
   ⚙️  Intermedio - Revisar y ajustar nombres
   🔧 Avanzado - Personalizar todo (nombres y tipos)
   🎯 Experto - Configurar cada columna individualmente
```

#### 🚀 Nivel Rápido (Automático)

```
⠦ Configurando columnas automáticamente...
✅ Configuración automática completada
```

#### ⚙️ Nivel Intermedio

```
📝 Revisión de Nombres de Columnas

Columna 1/20:
📋 Original: pnum
🔧 Sugerido: pnum_
📊 Ejemplos: [1105, 1392, 2094]

¿Usar nombre sugerido 'pnum_'? [y/n] (y): n
📝 Ingresa nombre personalizado: id
```

#### 🔧 Nivel Avanzado

```
🔧 Configurando: pnum

¿Usar nombre 'pnum_'? [y/n] (y): y

[?] Tipo SQL para 'pnum_' (detectado: INT):
 > ✅ Usar detectado: INT
   VARCHAR(255)
   DECIMAL(10,2)
   DATETIME
   TEXT
   BOOLEAN
```

#### 🎯 Nivel Experto

```
🎯 Columna 1 de 20
============================================================

╭───────────────────────────────── Información de Columna ─────────────────────────────────────╮
│                                                                                               │
│ 📋 Nombre Original: pnum                                                                      │
│ 📊 Tipo Pandas: int64                                                                        │
│ 🔢 Valores únicos: 875                                                                       │
│ ❓ Valores nulos: 0                                                                           │
│                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯

       📊 Estadísticas
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Estadística ┃ Valor          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Mínimo      │ 1105           │
│ Máximo      │ 999999         │
│ Promedio    │ 456789.25      │
└─────────────┴────────────────┘

🏷️  Configuración de Nombre:
Nombre para la columna (pnum_): id

🔧 Configuración de Tipo SQL:
💡 Tipo detectado: INT

[?] Selecciona categoría de tipo:
 > 🔢 Numérico
   📝 Texto
   📅 Fecha/Hora
   🔘 Otros
   ✅ Usar detectado: INT
```

### 6. 📋 Resumen de Configuración

```
📋 RESUMEN DE CONFIGURACIÓN
============================================================

╭─────────────────────────────── Configuración General ───────────────────────────────╮
│                                                                                      │
│ 📄 Archivo CSV: ../United-States-(Washington)-1,121,721.csv                         │
│ 🏷️  Nombre de tabla: profiles                                                        │
│ 🔢 Total de columnas: 20                                                            │
│                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────╯

           🏗️  Mapeo de Columnas
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Original                  ┃ SQL                       ┃ Tipo            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ pnum                      │ id                        │ INT             │
│ location_locality         │ city                      │ VARCHAR(50)     │
│ full_name                 │ name                      │ VARCHAR(100)    │
│ ...                       │ ...                       │ ...             │
└───────────────────────────┴───────────────────────────┴─────────────────┘

¿La configuración es correcta? [y/n] (y):
```

### 7. 🚀 Conversión con Progreso

**Selección de Cantidad:**

```
🚀 INICIANDO CONVERSIÓN
==================================================

[?] ¿Cuántas filas quieres convertir?:
 > 🧪 Muestra pequeña (100 filas)
   📊 Muestra mediana (5,000 filas)
   📈 Muestra grande (50,000 filas)
   🌍 Archivo completo
   🛠️  Cantidad personalizada
```

**Progreso Animado:**

```
⠦ Iniciando conversión...    ████████████████████░░░░░░░░░░░░░░░░░░░░  50%
⠦ Detectando estructura...   ██████████████████████████████████████░░  95%
⠦ Procesando datos...        ████████████████████████████████████████ 100%
```

### 8. 🎉 Resultados

**Panel de Resultados:**

```
╭─────────────────────────────────────── 🎉 Resultados ───────────────────────────────────────╮
│                                                                                              │
│ ✅ CONVERSIÓN EXITOSA                                                                        │
│                                                                                              │
│ 📄 Archivo SQL: United-States-Washington-1_121_721_custom_insert_statements.sql             │
│ 🗂️  Tabla SQL: profiles                                                                      │
│ 📊 Filas procesadas: 5000                                                                   │
│ 📏 Tamaño SQL: 3.45 MB                                                                      │
│ ⏱️  Tiempo: 2.34 segundos                                                                   │
│ ⚡ Velocidad: 2136 filas/segundo                                                            │
│                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 9. 📋 Preview del SQL

```
📋 PREVIEW DEL ARCHIVO SQL
──────────────────────────────────────────────────

🏗️  CREATE TABLE:
╭─────────────────────────────────────────────────────────────────────────────────────╮
│ CREATE TABLE profiles (                                                             │
│     id INT,                                                                         │
│     city VARCHAR(50),                                                               │
│     name VARCHAR(100),                                                              │
│     email VARCHAR(255),                                                             │
│     industry VARCHAR(100)                                                           │
│ );                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────╯

📝 PRIMEROS INSERT STATEMENTS: (mostrando 2 de 5000 total)
1. INSERT INTO profiles (id, city, name, email, industry) VALUES (1105, 'washington', 'john cajayon', 'john_cajayon@fanniemae.com', 'financial services');
2. INSERT INTO profiles (id, city, name, email, industry) VALUES (1392, 'washington', 'andre hoyrd', 'ahoyrd@udc.edu', 'education management');
...

🎉 ¡Conversión completada exitosamente!
📚 Consulta DATABASE_IMPORT_GUIDE.md para instrucciones de importación
```

---

## 🎯 Casos de Uso Recomendados

### 📊 Para Análisis de Datos Rápido

```bash
python cli_interactive.py
# Seleccionar: 🚀 Rápido + 🧪 Muestra pequeña (100 filas)
```

### 🏢 Para Producción

```bash
python cli_interactive.py
# Seleccionar: 🔧 Avanzado + 🌍 Archivo completo
```

### 🔬 Para Investigación Detallada

```bash
python cli_interactive.py
# Seleccionar: 🎯 Experto + 📊 Muestra mediana (5,000 filas)
```

### 🛠️ Para Desarrollo

```bash
python cli_interactive.py
# Seleccionar: ⚙️ Intermedio + 📈 Muestra grande (50,000 filas)
```

---

## 🚨 Consejos y Mejores Prácticas

### ⚡ Rendimiento

- **Archivos grandes**: Usa muestras primero para probar la configuración
- **Memoria limitada**: Selecciona chunks más pequeños (500-1000 filas)
- **SSD recomendado**: Para archivos > 100MB

### 🎨 Personalización

- **Nombres de columnas**: Evita espacios y caracteres especiales
- **Tipos SQL**: VARCHAR(255) es seguro para texto variable
- **Tabla**: Usa nombres descriptivos y cortos

### 🔍 Validación

- **Siempre revisa el preview** antes de procesar archivos completos
- **Verifica tipos de datos** especialmente para números y fechas
- **Guarda configuraciones** para archivos similares

### 🛡️ Seguridad

- **Escapa caracteres especiales**: El sistema lo hace automáticamente
- **Valida datos sensibles**: Revisa antes de importar a producción
- **Backup**: Siempre haz respaldo antes de importar datos

---

## 🔧 Opciones Avanzadas

### 📝 Tipos SQL Disponibles

| Categoría         | Tipos Disponibles                                        |
| ----------------- | -------------------------------------------------------- |
| **📝 Texto**      | VARCHAR(50), VARCHAR(255), VARCHAR(1000), TEXT, LONGTEXT |
| **🔢 Numérico**   | INT, BIGINT, DECIMAL(10,2), DECIMAL(15,4), FLOAT, DOUBLE |
| **📅 Fecha/Hora** | DATE, DATETIME, TIMESTAMP, TIME                          |
| **🔘 Otros**      | BOOLEAN, JSON, BLOB                                      |

### 🎛️ Configuraciones Personalizadas

**Tipos Personalizados:**

```sql
-- Ejemplos de tipos personalizados
ENUM('valor1', 'valor2', 'valor3')
DECIMAL(18,4)
VARCHAR(500)
```

### 📊 Estadísticas Disponibles (Modo Experto)

**Para Columnas Numéricas:**

- Mínimo, Máximo, Promedio
- Desviación estándar
- Percentiles

**Para Columnas de Texto:**

- Valores más frecuentes
- Longitud promedio
- Caracteres únicos

---

## 🎮 Atajos de Teclado

| Tecla    | Acción                 |
| -------- | ---------------------- |
| `↑/↓`    | Navegar opciones       |
| `Enter`  | Seleccionar            |
| `Ctrl+C` | Cancelar proceso       |
| `y/n`    | Confirmaciones rápidas |

---

## 🔄 Comparación con Versión Anterior

| Característica      | CLI Interactivo v2.0 | Versión Anterior   |
| ------------------- | -------------------- | ------------------ |
| **Interfaz**        | 🎨 Rica y colorida   | 📝 Texto plano     |
| **Personalización** | 🎯 4 niveles         | ⚙️ Limitada        |
| **Preview**         | 📊 Visual completo   | 📝 Líneas de texto |
| **Progreso**        | 📈 Barras animadas   | 🔢 Porcentajes     |
| **Validación**      | ✅ Tiempo real       | ❌ Post-proceso    |
| **Facilidad**       | 🚀 Muy fácil         | 🔧 Técnico         |

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo interrumpir el proceso?**
R: Sí, usa `Ctrl+C` en cualquier momento para cancelar de forma segura.

**P: ¿Se guardan mis configuraciones?**
R: No automáticamente, pero puedes copiar la configuración del resumen mostrado.

**P: ¿Funciona con archivos muy grandes?**
R: Sí, procesa por chunks para optimizar memoria.

**P: ¿Qué hago si hay errores?**
R: El sistema muestra mensajes descriptivos y opciones de corrección.

**P: ¿Puedo usar nombres de columnas con espacios?**
R: Se recomienda evitarlos, pero el sistema los convierte automáticamente.

---

**🎉 ¡Disfruta convirtiendo tus CSV con estilo!**
