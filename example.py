#!/usr/bin/env python3
"""
Script de ejemplo para convertir el archivo CSV a SQL
"""

from csv_to_sql import CSVToSQLConverter
import os


def convert_washington_data():
    """Convierte el archivo de datos de Washington a SQL"""

    # Ruta al archivo CSV
    csv_file = "../United-States-(Washington)-1,121,721.csv"

    # Verificar que el archivo existe
    if not os.path.exists(csv_file):
        print(f"Error: No se encontró el archivo {csv_file}")
        return

    print("=== Convertidor CSV a SQL ===")
    print(f"Archivo CSV: {csv_file}")

    # Crear convertidor
    converter = CSVToSQLConverter(
        csv_file_path=csv_file,
        table_name="washington_data",  # Nombre personalizado para la tabla
    )

    # Opciones de conversión
    chunk_size = 1000  # Procesar 1000 filas a la vez
    max_rows = 10000  # Limitar a 10,000 filas para prueba (None para todas)

    print(f"Procesando en chunks de {chunk_size} filas...")
    if max_rows:
        print(f"Limitado a {max_rows} filas para prueba")

    try:
        # Convertir a SQL
        sql_file = converter.convert_to_sql(chunk_size=chunk_size, max_rows=max_rows)

        print("\n✅ Conversión completada exitosamente!")
        print(f"📄 Archivo SQL generado: {sql_file}")
        print(f"📊 Tabla SQL: {converter.table_name}")

        # Mostrar información del archivo generado
        if os.path.exists(sql_file):
            file_size = os.path.getsize(sql_file) / 1024 / 1024  # MB
            print(f"📏 Tamaño del archivo SQL: {file_size:.2f} MB")

            # Mostrar las primeras líneas del archivo SQL
            print("\n📋 Primeras líneas del archivo SQL:")
            print("-" * 50)
            with open(sql_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 20:  # Mostrar solo las primeras 20 líneas
                        print("...")
                        break
                    print(line.rstrip())

    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")


def convert_full_data():
    """Convierte todo el archivo CSV (puede tomar mucho tiempo)"""

    csv_file = "../United-States-(Washington)-1,121,721.csv"

    if not os.path.exists(csv_file):
        print(f"Error: No se encontró el archivo {csv_file}")
        return

    print("=== Conversión COMPLETA del archivo CSV ===")
    print(
        "⚠️  ADVERTENCIA: Esto puede tomar mucho tiempo y generar un archivo muy grande"
    )

    response = input("¿Estás seguro de que quieres procesar TODO el archivo? (y/N): ")

    if response.lower() not in ["y", "yes", "sí", "si"]:
        print("Conversión cancelada.")
        return

    converter = CSVToSQLConverter(
        csv_file_path=csv_file, table_name="washington_complete_data"
    )

    try:
        sql_file = converter.convert_to_sql(chunk_size=5000)  # Chunks más grandes
        print("\n✅ Conversión completa exitosa!")
        print(f"📄 Archivo SQL: {sql_file}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("Selecciona una opción:")
    print("1. Convertir muestra (10,000 filas)")
    print("2. Convertir archivo completo")
    print("3. Salir")

    choice = input("\nOpción (1-3): ").strip()

    if choice == "1":
        convert_washington_data()
    elif choice == "2":
        convert_full_data()
    elif choice == "3":
        print("¡Hasta luego!")
    else:
        print("Opción inválida.")
