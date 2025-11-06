# Changelog

Todos los cambios notables a este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Añadido
- Pendiente para próximas versiones

### Cambiado
- Pendiente para próximas versiones

### Arreglado
- Pendiente para próximas versiones

## [1.0.0] - 2025-11-06

### Añadido
- ✨ Conversión eficiente de archivos CSV a SQL con procesamiento por chunks
- 🔍 Detección automática de tipos de datos SQL (VARCHAR, INT, DECIMAL, BOOLEAN, TEXT, DATETIME)
- 🛡️ Generación segura de nombres de tabla SQL válidos
- 🔄 Escape automático de caracteres especiales para prevenir errores SQL
- 📊 Logging detallado del proceso de conversión con timestamps
- ⚙️ Opciones flexibles de configuración (chunk_size, max_rows, table_name personalizado)
- 🖥️ Interfaz de línea de comandos (CLI) interactiva con inquirer
- 📁 Múltiples scripts de ejemplo y uso
- 🗄️ Soporte para importación a MySQL, PostgreSQL y SQLite
- 📚 Documentación completa con guías de uso e importación

### Características Técnicas
- Procesamiento eficiente en memoria para archivos grandes
- Detección inteligente de tipos de datos basada en contenido
- Generación de estructura SQL completa (DROP TABLE, CREATE TABLE, INSERT statements)
- Manejo robusto de errores y logging
- Soporte para múltiples formatos de fecha/hora
- Validación de nombres de columnas y tabla

### Archivos Principales
- `csv_to_sql.py` - Módulo principal con clase CSVToSQLConverter
- `cli_interactive.py` - CLI interactivo con rich y inquirer
- `main.py` - Script principal de ejecución
- `example.py` - Ejemplos de uso programático
- `DATABASE_IMPORT_GUIDE.md` - Guía detallada de importación a bases de datos

### Dependencias
- pandas >= 1.5.0 - Procesamiento de datos
- numpy >= 1.21.0 - Operaciones numéricas
- click >= 8.0.0 - CLI framework
- rich >= 13.0.0 - Output formatting
- inquirer >= 3.0.0 - Interactive prompts