#!/usr/bin/env python3
"""
Demo script para probar la funcionalidad COPY sin interacción.
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from sql_repair_fixed import extract_copy_statement, parse_create_table


def test_copy_functionality():
    """Prueba la funcionalidad COPY con el archivo test_sample.sql"""

    print("🚀 Probando funcionalidad COPY...")

    # Leer archivo de prueba
    sql_file = "../test_sample.sql"
    if not os.path.exists(sql_file):
        print(f"❌ No se encuentra: {sql_file}")
        return

    with open(sql_file, "r", encoding="utf-8", errors="ignore") as f:
        sql_text = f.read()

    print(f"📄 Archivo leído: {len(sql_text)} caracteres")

    # Parsear estructura
    try:
        table_name, columns = parse_create_table(sql_text)
        print(f"📋 Tabla detectada: {table_name}")
        print(f"📊 Columnas detectadas: {len(columns)}")
    except ValueError as e:
        print(f"❌ Error parseando: {e}")
        return

    # Usar solo algunas columnas para la prueba
    selected_columns = [
        ("linkedin_url_id", "VARCHAR(255)"),
        ("company_name", "VARCHAR(255)"),
        ("industry", "VARCHAR(255)"),
        ("country_code", "VARCHAR(255)"),
        ("website", "VARCHAR(255)"),
    ]

    column_names = [col[0] for col in selected_columns]
    column_types = [col[1] for col in selected_columns]

    # Índices de las columnas que queremos mantener (0-based)
    # linkedin_url_id=2, company_name=3, industry=4, country_code=11, website=12
    kept_indices = [2, 3, 4, 11, 12]

    print(f"✅ Usando columnas: {column_names}")

    # Generar COPY statement
    copy_sql = extract_copy_statement(
        sql_text,
        "test_companies",
        column_names,
        max_values=5,  # Solo 5 registros para prueba
        kept_indices=kept_indices,
        column_types=column_types,
    )

    if copy_sql.strip():
        print("🎉 ¡COPY statement generado exitosamente!")
        print("📄 Guardando en: test_copy_output.sql")

        # Guardar resultado
        with open("test_copy_output.sql", "w", encoding="utf-8") as f:
            f.write("-- DEMO de funcionalidad COPY\n")
            f.write("-- Generado automáticamente\n\n")

            # CREATE TABLE
            f.write("DROP TABLE IF EXISTS test_companies;\n\n")
            f.write("CREATE TABLE test_companies (\n")
            for i, (name, type_sql) in enumerate(selected_columns):
                comma = "," if i < len(selected_columns) - 1 else ""
                f.write(f"    {name} {type_sql}{comma}\n")
            f.write(");\n\n")

            # COPY statement
            f.write(copy_sql)

        print("✅ Archivo generado: test_copy_output.sql")

        # Mostrar primeras líneas del resultado
        print("\n📋 Primeras líneas del COPY statement:")
        print("-" * 60)
        lines = copy_sql.split("\n")
        for i, line in enumerate(lines[:10]):
            print(f"{i + 1:2}: {line}")
        if len(lines) > 10:
            print(f"... ({len(lines) - 10} líneas más)")

    else:
        print("❌ No se pudo generar COPY statement")


if __name__ == "__main__":
    test_copy_functionality()
