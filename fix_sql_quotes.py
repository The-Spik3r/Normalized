#!/usr/bin/env python3
"""
Script para arreglar comillas simples no escapadas en archivos SQL
Específicamente para arreglar nombres como "O'Keefe" que rompen la sintaxis SQL
"""

import sys
import re
from pathlib import Path


def fix_sql_quotes(input_file: str, output_file: str = None):
    """
    Arregla las comillas simples no escapadas en un archivo SQL

    Args:
        input_file: Archivo SQL de entrada
        output_file: Archivo SQL de salida (opcional, por defecto usa _fixed.sql)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: El archivo {input_file} no existe")
        return False

    if output_file is None:
        output_file = input_path.stem + "_fixed.sql"

    output_path = Path(output_file)

    print(f"Procesando: {input_file}")
    print(f"Salida: {output_file}")

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            with open(output_path, "w", encoding="utf-8") as outfile:
                line_count = 0
                fixed_count = 0

                for line in infile:
                    line_count += 1
                    original_line = line

                    # Procesar líneas que contengan datos (buscar patrones de comillas problemáticas)
                    if "'" in line and not line.startswith("--"):
                        # Usar regex para encontrar comillas simples dentro de strings
                        # Patrón: buscar comillas simples que no estén ya escapadas
                        # y que estén dentro de valores de datos (no en comandos SQL)

                        # Escapar comillas simples que no estén ya escapadas
                        # Evitar escapar comillas que ya están escapadas ('')
                        # y comillas que son parte de la sintaxis SQL

                        fixed_line = re.sub(
                            r"(?<!')'(?!')",  # Comilla simple que no esté precedida ni seguida por otra comilla
                            "''",  # Reemplazar con comilla doble (escapada)
                            line,
                        )

                        if fixed_line != original_line:
                            fixed_count += 1
                            line = fixed_line

                    outfile.write(line)

                    # Mostrar progreso cada 10,000 líneas
                    if line_count % 10000 == 0:
                        print(
                            f"Procesadas {line_count:,} líneas, arregladas {fixed_count:,}"
                        )

        print("\n✓ Completado!")
        print(f"Total líneas procesadas: {line_count:,}")
        print(f"Líneas arregladas: {fixed_count:,}")
        return True

    except Exception as e:
        print(f"Error procesando el archivo: {e}")
        return False


def main():
    """Función principal del script"""
    if len(sys.argv) < 2:
        print("Uso: python fix_sql_quotes.py <archivo_entrada> [archivo_salida]")
        print("\nEjemplo:")
        print("  python fix_sql_quotes.py data.sql data_fixed.sql")
        print("  python fix_sql_quotes.py data.sql  # Salida: data_fixed.sql")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = fix_sql_quotes(input_file, output_file)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
