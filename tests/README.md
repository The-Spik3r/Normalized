# Tests para CSV to SQL Converter

Este directorio contiene los tests del proyecto.

## Estructura de tests

- `test_csv_to_sql.py`: Tests del módulo principal
- `test_cli.py`: Tests de la interfaz de línea de comandos
- `fixtures/`: Archivos de prueba y datos de ejemplo

## Ejecutar tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=csv_to_sql

# Ejecutar tests específicos
pytest tests/test_csv_to_sql.py
```
