"""
Test para verificar que la lectura de JSON maneja correctamente los arrays
"""

import sys

sys.path.insert(0, "csv-to-sql-project")

from cli_interactive import read_jsonl_to_dataframe

# Leer el archivo de muestra
df = read_jsonl_to_dataframe("sample_50.json", nrows=10)

print(f"\n{'=' * 60}")
print(f"Total registros leídos: {len(df)}")
print(f"Columnas: {df.columns.tolist()}")
print(f"{'=' * 60}\n")

# Verificar que 'e' y 't' sean strings, no listas
print("Primeros 5 registros:")
print(df.head())

print("\n" + "=" * 60)
print("Tipos de datos:")
print(df.dtypes)

print("\n" + "=" * 60)
print("Ejemplos de emails (campo 'e'):")
for i, val in enumerate(df["e"].head(10)):
    print(f"  {i + 1}. {val} (tipo: {type(val).__name__})")

if "t" in df.columns:
    print("\n" + "=" * 60)
    print("Ejemplos de teléfonos (campo 't'):")
    for i, val in enumerate(df["t"].head(10)):
        if val is not None:
            print(f"  {i + 1}. {val} (tipo: {type(val).__name__})")
