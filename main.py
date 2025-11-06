#!/usr/bin/env python3
"""
Script final para conversión CSV a SQL
Este script demuestra el uso completo del convertidor
"""

import os
import sys
from csv_to_sql import CSVToSQLConverter
from datetime import datetime


def main():
    print("=" * 60)
    print("🚀 CONVERTIDOR CSV A SQL - PROYECTO COMPLETO")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configuración del archivo
    csv_file = "../United-States-(Washington)-1,121,721.csv"

    # Verificar archivo
    if not os.path.exists(csv_file):
        print("❌ Error: No se encontró el archivo CSV")
        print(f"   Buscando: {os.path.abspath(csv_file)}")
        return 1

    # Mostrar información del archivo
    file_size = os.path.getsize(csv_file) / 1024 / 1024  # MB
    print(f"📄 Archivo CSV: {csv_file}")
    print(f"📏 Tamaño: {file_size:.2f} MB")
    print()

    # Opciones de conversión
    print("🔧 OPCIONES DISPONIBLES:")
    print("1. 🧪 Muestra pequeña (100 filas) - Para pruebas rápidas")
    print("2. 📊 Muestra mediana (5,000 filas) - Para validación")
    print("3. 📈 Muestra grande (50,000 filas) - Para desarrollo")
    print("4. 🌍 Archivo completo (1,121,721 filas) - Producción")
    print("5. 🛠️  Modo personalizado")
    print("6. ❌ Salir")
    print()

    while True:
        choice = input("Selecciona una opción (1-6): ").strip()

        if choice == "1":
            convert_sample(csv_file, 100, "test_data")
            break
        elif choice == "2":
            convert_sample(csv_file, 5000, "validation_data")
            break
        elif choice == "3":
            convert_sample(csv_file, 50000, "development_data")
            break
        elif choice == "4":
            convert_full(csv_file)
            break
        elif choice == "5":
            convert_custom(csv_file)
            break
        elif choice == "6":
            print("👋 ¡Hasta luego!")
            return 0
        else:
            print("⚠️  Opción inválida. Intenta de nuevo.")


def convert_sample(csv_file: str, max_rows: int, table_suffix: str):
    """Convierte una muestra del archivo CSV"""
    print(f"\n🔄 Procesando muestra de {max_rows:,} filas...")

    table_name = f"washington_{table_suffix}"

    try:
        converter = CSVToSQLConverter(csv_file, table_name)

        start_time = datetime.now()
        sql_file = converter.convert_to_sql(
            chunk_size=min(1000, max_rows // 10), max_rows=max_rows
        )
        end_time = datetime.now()

        # Mostrar resultados
        duration = (end_time - start_time).total_seconds()
        sql_size = os.path.getsize(sql_file) / 1024 / 1024  # MB

        print("\n✅ CONVERSIÓN EXITOSA")
        print("-" * 40)
        print(f"📄 Archivo SQL: {sql_file}")
        print(f"🗂️  Tabla SQL: {table_name}")
        print(f"📊 Filas procesadas: {max_rows:,}")
        print(f"📏 Tamaño SQL: {sql_size:.2f} MB")
        print(f"⏱️  Tiempo: {duration:.2f} segundos")
        print(f"⚡ Velocidad: {max_rows / duration:.0f} filas/segundo")

        show_sql_preview(sql_file)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def convert_full(csv_file: str):
    """Convierte el archivo completo"""
    print("\n⚠️  CONVERSIÓN COMPLETA DEL ARCHIVO")
    print("Esto procesará más de 1 millón de filas y puede:")
    print("- Tomar 10-30 minutos")
    print("- Generar un archivo SQL de 500+ MB")
    print("- Usar mucha memoria y CPU")
    print()

    confirm = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ")

    if confirm != "CONFIRMAR":
        print("❌ Conversión cancelada")
        return

    print("\n🚀 Iniciando conversión completa...")
    print("💡 Puedes interrumpir con Ctrl+C si es necesario")

    try:
        converter = CSVToSQLConverter(csv_file, "washington_complete_dataset")

        start_time = datetime.now()
        sql_file = converter.convert_to_sql(chunk_size=2000)  # Chunks más grandes
        end_time = datetime.now()

        # Mostrar resultados
        duration = (end_time - start_time).total_seconds()
        sql_size = os.path.getsize(sql_file) / 1024 / 1024  # MB

        print("\n🎉 CONVERSIÓN COMPLETA EXITOSA")
        print("=" * 50)
        print(f"📄 Archivo SQL: {sql_file}")
        print("🗂️  Tabla SQL: washington_complete_dataset")
        print("📊 Filas procesadas: 1,121,721")
        print(f"📏 Tamaño SQL: {sql_size:.2f} MB")
        print(f"⏱️  Tiempo total: {duration / 60:.1f} minutos")
        print(f"⚡ Velocidad promedio: {1121721 / duration:.0f} filas/segundo")

    except KeyboardInterrupt:
        print("\n⚠️  Conversión interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def convert_custom(csv_file: str):
    """Conversión con parámetros personalizados"""
    print("\n🛠️  MODO PERSONALIZADO")
    print("-" * 30)

    try:
        # Solicitar parámetros
        table_name = input("Nombre de la tabla SQL (enter para auto): ").strip() or None

        max_rows_input = input("Máximo de filas (enter para todas): ").strip()
        max_rows = int(max_rows_input) if max_rows_input else None

        chunk_size_input = input("Tamaño del chunk (enter para 1000): ").strip()
        chunk_size = int(chunk_size_input) if chunk_size_input else 1000

        print("\n🔄 Configuración:")
        print(f"   Tabla: {table_name or 'Auto-generado'}")
        print(f"   Filas máximas: {max_rows or 'Todas'}")
        print(f"   Chunk size: {chunk_size}")

        confirm = input("\n¿Proceder? (y/N): ")
        if confirm.lower() not in ["y", "yes", "sí", "si"]:
            print("❌ Conversión cancelada")
            return

        # Ejecutar conversión
        converter = CSVToSQLConverter(csv_file, table_name)

        start_time = datetime.now()
        sql_file = converter.convert_to_sql(chunk_size, max_rows)
        end_time = datetime.now()

        # Mostrar resultados
        duration = (end_time - start_time).total_seconds()
        sql_size = os.path.getsize(sql_file) / 1024 / 1024

        print("\n✅ CONVERSIÓN PERSONALIZADA EXITOSA")
        print("-" * 40)
        print(f"📄 Archivo SQL: {sql_file}")
        print(f"🗂️  Tabla SQL: {converter.table_name}")
        print(f"📏 Tamaño SQL: {sql_size:.2f} MB")
        print(f"⏱️  Tiempo: {duration:.2f} segundos")

    except ValueError as e:
        print(f"❌ Error en los parámetros: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def show_sql_preview(sql_file: str):
    """Muestra una vista previa del archivo SQL"""
    print("\n📋 VISTA PREVIA DEL SQL:")
    print("-" * 40)

    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Mostrar CREATE TABLE
        create_start = next(i for i, line in enumerate(lines) if "CREATE TABLE" in line)
        create_end = (
            next(i for i, line in enumerate(lines[create_start:]) if ");" in line)
            + create_start
            + 1
        )

        print("🏗️  CREATE TABLE:")
        for line in lines[create_start:create_end]:
            print(f"   {line.rstrip()}")

        # Mostrar algunos INSERT
        insert_lines = [line for line in lines if line.startswith("INSERT")]
        print(f"\n📝 PRIMEROS INSERT STATEMENTS (de {len(insert_lines)} total):")
        for i, line in enumerate(insert_lines[:3]):
            print(f"   {line.rstrip()}")

        if len(insert_lines) > 3:
            print("   ...")

    except Exception as e:
        print(f"   ❌ Error mostrando vista previa: {e}")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
