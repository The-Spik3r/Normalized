# Guía de Contribución

¡Gracias por tu interés en contribuir al proyecto CSV to SQL Converter!

## Cómo contribuir

### 1. Fork del repositorio

1. Haz un fork del repositorio
2. Clona tu fork localmente
3. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`

### 2. Configuración del entorno de desarrollo

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/csv-to-sql-converter.git
cd csv-to-sql-converter

# Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt
pip install -e .[dev]  # Para dependencias de desarrollo
```

### 3. Estándares de código

- Usa **Black** para formatear el código: `black .`
- Usa **flake8** para linting: `flake8 .`
- Agrega tests para nuevas funcionalidades
- Documenta funciones y clases importantes

### 4. Tests

```bash
# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=csv_to_sql
```

### 5. Envío de cambios

1. Asegúrate de que todos los tests pasan
2. Actualiza la documentación si es necesario
3. Haz commit de tus cambios con mensajes descriptivos
4. Push a tu fork: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

## Tipos de contribuciones

- 🐛 **Bug fixes**: Corrección de errores
- ✨ **Features**: Nuevas funcionalidades
- 📝 **Documentación**: Mejoras en la documentación
- 🎨 **Refactoring**: Mejoras en el código sin cambiar funcionalidad
- ⚡ **Performance**: Optimizaciones de rendimiento

## Reportar bugs

Usa las [GitHub Issues](https://github.com/tu-usuario/csv-to-sql-converter/issues) para reportar bugs. Incluye:

- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Información del sistema (OS, Python version, etc.)

## Solicitar features

Abre una issue describiendo:

- La funcionalidad que necesitas
- Por qué sería útil
- Posibles implementaciones

¡Gracias por contribuir! 🚀
