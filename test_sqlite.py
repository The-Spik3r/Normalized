#!/usr/bin/env python3
import sqlite3
import os

# Verificar que existe la base de datos
db_file = "25m_corrected.db"
if os.path.exists(db_file):
    print(f"✅ Base de datos encontrada: {db_file}")
    print(f"📊 Tamaño: {os.path.getsize(db_file) / 1024:.2f} KB")

    # Conectar y consultar
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Contar registros totales
    cursor.execute("SELECT COUNT(*) FROM imported_data")
    total = cursor.fetchone()[0]
    print(f"📈 Registros totales: {total}")

    # Mostrar estructura de la tabla
    cursor.execute("PRAGMA table_info(imported_data)")
    columns = cursor.fetchall()
    print(f"🏗️ Columnas en la tabla ({len(columns)} total):")
    for col in columns[:5]:  # Mostrar solo las primeras 5
        print(f"  - {col[1]} ({col[2]})")
    if len(columns) > 5:
        print(f"  ... y {len(columns) - 5} columnas más")

    # Mostrar algunas empresas de ejemplo
    cursor.execute("SELECT company_name, domain FROM imported_data LIMIT 5")
    rows = cursor.fetchall()
    print(f"🏢 Primeras empresas:")
    for row in rows:
        print(f"  - {row[0]}: {row[1]}")

    conn.close()
    print("\n🎉 ¡Base de datos SQLite funciona correctamente!")
else:
    print(f"❌ No se encontró la base de datos: {db_file}")
