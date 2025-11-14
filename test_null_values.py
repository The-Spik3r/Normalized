#!/usr/bin/env python3
"""
Test específico para verificar el manejo de valores NULL en COPY statements
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sql_repair_fixed import extract_copy_statement


def test_null_values():
    """Prueba específica para valores NULL"""

    print("🧪 Probando manejo de valores NULL...")

    # SQL de prueba con valores NULL explícitos
    test_sql = """
    (1001, 'test.com', 'test-company', 'Test Company', 'Technology', 'null', 'Test Description', 'null', 'us'),
    (1002, 'example.org', 'null', 'Example Corp', 'null', 'Finance', 'null', 'Some description', 'ca'),
    (1003, 'null', 'demo-inc', 'null', 'Healthcare', 'Medical', 'Demo company', 'null', 'null')
    """

    column_names = [
        "id",
        "domain",
        "linkedin_id",
        "name",
        "industry",
        "category",
        "description",
        "extra",
        "country",
    ]
    column_types = [
        "INTEGER",
        "VARCHAR(255)",
        "VARCHAR(255)",
        "VARCHAR(255)",
        "VARCHAR(255)",
        "VARCHAR(255)",
        "TEXT",
        "VARCHAR(255)",
        "VARCHAR(2)",
    ]

    print(f"📊 Columnas: {len(column_names)}")
    print(f"📋 Datos de prueba con valores 'null' explícitos")

    # Generar COPY statement
    copy_sql = extract_copy_statement(
        test_sql,
        "test_null_handling",
        column_names,
        max_values=0,  # Todos los registros
        kept_indices=None,  # Todas las columnas
        column_types=column_types,
    )

    if copy_sql.strip():
        print("🎉 ¡COPY statement generado!")

        # Guardar resultado
        with open("test_null_handling.sql", "w", encoding="utf-8") as f:
            f.write("-- Test de manejo de valores NULL\n")
            f.write("-- Los valores 'null' deben convertirse a \\N\n\n")
            f.write("DROP TABLE IF EXISTS test_null_handling;\n\n")
            f.write("CREATE TABLE test_null_handling (\n")
            for i, (name, type_sql) in enumerate(zip(column_names, column_types)):
                comma = "," if i < len(column_names) - 1 else ""
                f.write(f"    {name} {type_sql}{comma}\n")
            f.write(");\n\n")
            f.write(copy_sql)

        print("✅ Archivo generado: test_null_handling.sql")

        # Mostrar resultado para verificar
        print("\n📋 COPY statement generado:")
        print("-" * 80)
        lines = copy_sql.split("\n")
        for i, line in enumerate(lines):
            if line.strip():  # Solo líneas no vacías
                print(f"{i + 1:2}: {line}")

        # Verificar específicamente los NULL
        data_lines = [line for line in lines if line.startswith("'") or "\\N" in line]
        print(f"\n🔍 Verificando conversión de NULL:")
        print("-" * 50)
        for i, line in enumerate(data_lines):
            null_count = line.count("\\N")
            print(f"Fila {i + 1}: {null_count} valores NULL (\\N)")
            if null_count > 0:
                print(f"         {line[:100]}{'...' if len(line) > 100 else ''}")

    else:
        print("❌ No se pudo generar COPY statement")


if __name__ == "__main__":
    test_null_values()
