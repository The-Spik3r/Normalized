# CSV to SQL Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Este proyecto convierte archivos CSV grandes a archivos SQL con declaraciones INSERT, optimizado para manejar archivos de gran tamaño de manera eficiente.

## 🚀 Características Principales

## 🚀 Características Principales

- ✅ **Procesamiento eficiente**: Maneja archivos CSV grandes usando chunks
- ✅ **Detección automática de tipos**: Detecta automáticamente los tipos de datos SQL
- ✅ **Nombres de tabla seguros**: Genera nombres de tabla válidos para SQL
- ✅ **Escape de caracteres**: Escapa correctamente los valores para evitar errores SQL
- ✅ **Logging detallado**: Registro completo del proceso de conversión
- ✅ **Opciones flexibles**: Permite limitar filas y personalizar el procesamiento

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
git clone https://github.com/tu-usuario/csv-to-sql-converter.git
cd csv-to-sql-converter
pip install -r requirements.txt
```

### Método 2: Instalación directa

```bash
pip install git+https://github.com/tu-usuario/csv-to-sql-converter.git
```

## 📖 Uso Rápido

### Opción 1: Script de ejemplo

```bash
python example.py
```

### Opción 2: Línea de comandos

```bash
# Convertir archivo completo
python csv_to_sql.py "../United-States-(Washington)-1,121,721.csv"

# Con opciones personalizadas
python csv_to_sql.py "../United-States-(Washington)-1,121,721.csv" --table-name mi_tabla --max-rows 5000
```

### Opción 3: Como módulo Python

```python
from csv_to_sql import CSVToSQLConverter

# Crear convertidor
converter = CSVToSQLConverter(
    csv_file_path="tu_archivo.csv",
    table_name="mi_tabla"
)

# Convertir a SQL
sql_file = converter.convert_to_sql(
    chunk_size=1000,
    max_rows=10000  # None para procesar todas las filas
)

print(f"Archivo SQL creado: {sql_file}")
```

## ⚙️ Parámetros

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

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

- 📝 [Crear un Issue](https://github.com/tu-usuario/csv-to-sql-converter/issues)
- 📖 Lee la [documentación completa](DATABASE_IMPORT_GUIDE.md)
- 💡 Revisa los [ejemplos](example.py)

## ⭐ ¿Te gusta el proyecto?

¡Dale una estrella en GitHub! ⭐

---

**Desarrollado con ❤️ para la comunidad de desarrolladores**
