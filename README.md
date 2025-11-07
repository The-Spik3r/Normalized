# CSV to SQL Converter - Interactive CLI 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Rich CLI](https://img.shields.io/badge/CLI-Rich-purple.svg)](https://github.com/Textualize/rich)

**Convierte archivos CSV grandes a SQL con una interfaz interactiva hermosa y personalización completa.**

## ✨ Características Principales v2.0

- 🎨 **Interfaz CLI Interactiva**: Navegación intuitiva con menús y animaciones
- 🔧 **Personalización Total**: Control completo sobre nombres de tablas y columnas
- 📊 **Análisis Inteligente**: Preview automático de datos y tipos SQL
- ⚡ **4 Niveles de Configuración**: Desde automático hasta control experto
- 🎯 **Detección Automática**: Tipos de datos SQL inteligentes
- 📈 **Barras de Progreso**: Animaciones y feedback visual en tiempo real
- 🛡️ **Validación Robusta**: Verificación de entrada y manejo de errores
- 📋 **Preview de Resultados**: Vista previa del SQL generado

## 📋 Requisitos

- Python 3.8 o superior
- pandas >= 1.5.0
- numpy >= 1.21.0
- click >= 8.0.0
- rich >= 13.0.0
- inquirer >= 3.0.0

## 🔧 Instalación

### Método 1: Clonar el repositorio

```bash
git clone https://github.com/The-Spik3r/Normalized.git
cd Normalized/csv-to-sql-project
pip install -r requirements.txt
```

### Método 2: Instalación manual de dependencias

```bash
pip install pandas numpy click rich inquirer
```

## 🎮 Uso del CLI Interactivo (Recomendado)

### 🚀 Inicio Rápido

```bash
python cli_interactive.py
```

**¡Eso es todo!** El CLI interactivo te guiará paso a paso:

1. **📁 Selección de Archivo**: Detecta automáticamente archivos CSV o permite especificar ruta
2. **🔍 Análisis**: Muestra preview de datos y estadísticas
3. **🏷️ Configuración de Tabla**: Nombre personalizado o automático
4. **🏗️ Configuración de Columnas**: 4 niveles de personalización
5. **🚀 Conversión**: Selecciona cantidad de filas y ejecuta
6. **📋 Resultados**: Preview del SQL generado

### 🎯 Niveles de Personalización

#### 🚀 **Rápido** - Automático (0 minutos)

- ✅ Configuración automática completa
- ✅ Detección inteligente de tipos
- ✅ Nombres de columnas limpiados

#### ⚙️ **Intermedio** - Revisar Nombres (2-5 minutos)

- ✅ Revisar y ajustar nombres de columnas
- ✅ Tipos detectados automáticamente
- ✅ Preview de datos por columna

#### 🔧 **Avanzado** - Control Total (5-10 minutos)

- ✅ Personalizar nombres Y tipos de datos
- ✅ Selección de tipos SQL específicos
- ✅ Validación en tiempo real

#### 🎯 **Experto** - Columna por Columna (10-20 minutos)

- ✅ Configurar cada columna individualmente
- ✅ Estadísticas detalladas por columna
- ✅ Tipos SQL personalizados avanzados

## 📖 Uso Tradicional (Línea de Comandos)

### Opción 1: Script principal con interfaz

```bash
python main.py
```

### Opción 2: Línea de comandos básica

```bash
python csv_to_sql.py "archivo.csv" --table-name mi_tabla --max-rows 5000
```

### Opción 3: Como módulo Python

```python
from csv_to_sql import CSVToSQLConverter

converter = CSVToSQLConverter("archivo.csv", "mi_tabla")
sql_file = converter.convert_to_sql(chunk_size=1000, max_rows=10000)
```

## 📚 Documentación Completa

### 🎮 Guías del CLI Interactivo

- **[🚀 Guía Completa del CLI](./CLI_INTERACTIVE_GUIDE.md)** - Tutorial paso a paso completo
- **[📚 Ejemplos Prácticos](./PRACTICAL_EXAMPLES.md)** - Casos de uso reales y plantillas
- **[🗃️ Guía de Importación a BD](./DATABASE_IMPORT_GUIDE.md)** - Instrucciones para diferentes bases de datos

### 📖 Documentación Técnica

- **[📋 README Principal](./README.md)** - Este archivo
- **[⚙️ Referencia API](./csv_to_sql.py)** - Documentación del código
- **[🔧 Configuración](./requirements.txt)** - Dependencias del proyecto

## ⚙️ Parámetros Técnicos

### CSVToSQLConverter

- `csv_file_path`: Ruta al archivo CSV
- `table_name`: Nombre de la tabla SQL (opcional, se genera automáticamente)

### convert_to_sql()

- `chunk_size`: Número de filas a procesar por vez (default: 1000)
- `max_rows`: Máximo número de filas a procesar (None para todas)

## 🗃️ Tipos de Datos Soportados

El convertidor detecta automáticamente los tipos de datos:

| Tipo Python/Pandas | Tipo SQL              |
| ------------------ | --------------------- |
| string/object      | VARCHAR(n) o DATETIME |
| int64/int32        | INT                   |
| float64/float32    | DECIMAL(10,2)         |
| bool               | BOOLEAN               |
| otros              | TEXT                  |

## Estructura del Archivo SQL Generado

```sql
-- Comentarios con información del archivo fuente
DROP TABLE IF EXISTS tabla_nombre;

CREATE TABLE tabla_nombre (
    columna1 VARCHAR(100),
    columna2 INT,
    columna3 DECIMAL(10,2)
);

INSERT INTO tabla_nombre (columna1, columna2, columna3) VALUES ('valor1', 123, 45.67);
INSERT INTO tabla_nombre (columna1, columna2, columna3) VALUES ('valor2', 456, 89.01);
-- ... más INSERT statements

-- Total de registros insertados: N
COMMIT;
```

## 📁 Estructura del Proyecto

```
csv-to-sql-converter/
├── csv_to_sql.py          # Módulo principal
├── cli_interactive.py     # CLI interactivo
├── main.py               # Script principal
├── example.py            # Ejemplos de uso
├── requirements.txt      # Dependencias
├── README.md            # Documentación
├── LICENSE              # Licencia MIT
├── CONTRIBUTING.md      # Guía de contribución
├── DATABASE_IMPORT_GUIDE.md  # Guía de importación
└── .gitignore          # Archivos ignorados por Git
```

## 🚀 Desarrollo y Contribución

¿Quieres contribuir? ¡Genial! Lee nuestra [Guía de Contribución](CONTRIBUTING.md).

### Configuración de desarrollo

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/csv-to-sql-converter.git
cd csv-to-sql-converter

# Crea entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala dependencias de desarrollo
pip install -r requirements.txt
pip install -e .[dev]
```

### Tests

```bash
pytest
pytest --cov=csv_to_sql  # Con cobertura
```

## 📊 Archivos Generados

- `{nombre_archivo}_insert_statements.sql`: Archivo SQL con las declaraciones INSERT
- `csv_to_sql.log`: Log del proceso de conversión

## 💡 Consejos para Archivos Grandes

1. **Usa chunks pequeños**: Para archivos muy grandes, usa `chunk_size=500` o menor
2. **Prueba primero**: Usa `max_rows=1000` para probar la conversión antes del archivo completo
3. **Monitorea el espacio**: El archivo SQL puede ser más grande que el CSV original
4. **Usa SSD**: Para mejor rendimiento con archivos grandes

## 🗄️ Importación a Bases de Datos

Una vez generado el archivo SQL, puedes:

1. **Importar a MySQL**:

   ```bash
   mysql -u usuario -p base_de_datos < archivo.sql
   ```

2. **Importar a PostgreSQL**:

   ```bash
   psql -U usuario -d base_de_datos -f archivo.sql
   ```

3. **Importar a SQLite**:
   ```bash
   sqlite3 base_de_datos.db < archivo.sql
   ```

## ⚠️ Manejo de Errores

El script incluye logging detallado y manejo de errores para:

- Archivos CSV malformados
- Problemas de memoria con archivos grandes
- Errores de escritura de archivos
- Caracteres especiales y encoding

## 🎬 Demostración Visual

### 🚀 CLI Interactivo en Acción

```bash
$ python cli_interactive.py

╔═══════════════════════════════════════════════════════════════╗
║    � CSV TO SQL CONVERTER - INTERACTIVE CLI 🚀               ║
╚═══════════════════════════════════════════════════════════════╝

📁 Archivos CSV encontrados:
  1. ../United-States-(Washington)-1,121,721.csv (353.3 MB)

🔍 Análisis completado: 20 columnas, 1M+ filas
🏷️  Tabla configurada: profiles
🏗️  Columnas personalizadas: 20/20
⚡ Conversión: 5,000 filas en 2.3 segundos

✅ ¡Archivo SQL generado exitosamente!
```

### 📊 Ejemplo de Resultado SQL

```sql
-- Generado por CSV to SQL Converter v2.0
DROP TABLE IF EXISTS profiles;

CREATE TABLE profiles (
    id INT,
    name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(50),
    industry VARCHAR(100)
);

INSERT INTO profiles (id, name, email, city, industry) VALUES
(1105, 'John Cajayon', 'john_cajayon@fanniemae.com', 'washington', 'financial services'),
(1392, 'Andre Hoyrd', 'ahoyrd@udc.edu', 'washington', 'education management');
-- ... más registros
```

## 🏆 Casos de Uso Exitosos

| Industria         | Archivo                             | Resultado                     |
| ----------------- | ----------------------------------- | ----------------------------- |
| **🏥 Healthcare** | patient_records.csv (500K filas)    | Base de datos médica completa |
| **🛒 E-commerce** | product_catalog.csv (50K productos) | Catálogo optimizado           |
| **🏦 Finanzas**   | transactions.csv (2M transacciones) | Sistema de reportes           |
| **📚 Educación**  | student_data.csv (100K estudiantes) | Plataforma académica          |

## 🎯 Próximas Características

- 🔄 **Configuraciones guardadas** - Reutilizar configuraciones
- 🔗 **Conexión directa a BD** - Importar sin archivo intermedio
- 📊 **Validación de datos** - Detección de inconsistencias
- 🎨 **Temas personalizados** - Personalizar colores del CLI
- 🌐 **Soporte multi-idioma** - Interfaz en español/inglés

## �📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuir

¡Las contribuciones son más que bienvenidas!

### 🛠️ Cómo Contribuir:

1. **Fork** el proyecto
2. **Crea** una rama (`git checkout -b feature/MiCaracteristica`)
3. **Commit** tus cambios (`git commit -m 'Añadir MiCaracteristica'`)
4. **Push** a la rama (`git push origin feature/MiCaracteristica`)
5. **Abre** un Pull Request

### 🎯 Áreas de Contribución:

- � **Reportar bugs** - Ayuda a mejorar la estabilidad
- 💡 **Nuevas características** - Sugiere funcionalidades
- 📖 **Documentación** - Mejora guías y ejemplos
- 🎨 **UI/UX** - Mejora la experiencia del usuario
- 🧪 **Testing** - Añade tests y casos de prueba

## 📞 Soporte y Contacto

### 🆘 ¿Necesitas Ayuda?

- 📝 [Crear un Issue](https://github.com/tu-usuario/csv-to-sql-converter/issues)
- 📖 Lee la [documentación completa](DATABASE_IMPORT_GUIDE.md)
- 💡 Revisa los [ejemplos](example.py)

## ⭐ ¿Te gusta el proyecto?

¡Dale una estrella en GitHub! ⭐

---

**Desarrollado con ❤️ para la comunidad de desarrolladores**
