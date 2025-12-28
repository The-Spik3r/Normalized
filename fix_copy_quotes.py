#!/usr/bin/env python3
"""
Script especializado para arreglar comillas simples en archivos SQL formato COPY
Específicamente diseñado para formato COPY FROM STDIN de PostgreSQL
"""

import sys
import re
from pathlib import Path


def fix_copy_quotes(input_file: str, output_file: str = None):
    """
    Arregla las comillas simples no escapadas en un archivo SQL formato COPY

    Args:
        input_file: Archivo SQL de entrada (formato COPY)
        output_file: Archivo SQL de salida (opcional, por defecto usa _fixed.sql)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: El archivo {input_file} no existe")
        return False

    if output_file is None:
        output_file = input_path.stem + "_copy_fixed.sql"

    output_path = Path(output_file)

    print(f"Procesando archivo COPY: {input_file}")
    print(f"Salida: {output_file}")

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            with open(output_path, "w", encoding="utf-8") as outfile:
                line_count = 0
                fixed_count = 0

                for line in infile:
                    line_count += 1
                    original_line = line

                    # Procesar solo líneas de datos COPY (tienen tabs, no son comentarios ni comandos)
                    if (
                        "\t" in line
                        and not line.startswith("--")
                        and not line.startswith("COPY")
                        and not line.startswith("BEGIN")
                        and not line.startswith("COMMIT")
                        and line.strip() not in [".", "\\."]
                    ):
                        # Esta es una línea de datos en formato COPY
                        parts = line.rstrip("\n\r").split("\t")
                        fixed_parts = []
                        line_was_modified = False

                        for part in parts:
                            part = part.strip()

                            if part == "\\N":
                                # Es NULL en formato COPY, mantener como está
                                fixed_parts.append(part)
                            elif (
                                part.startswith("'")
                                and part.endswith("'")
                                and len(part) >= 2
                            ):
                                # Ya tiene comillas externas, revisar contenido interno
                                inner_content = part[1:-1]  # Remover comillas externas

                                # Contar comillas simples en el contenido
                                single_quotes = inner_content.count("'")
                                double_quotes = inner_content.count("''")

                                # Si hay comillas simples que no están escapadas
                                if single_quotes > 0 and single_quotes > (
                                    double_quotes * 2
                                ):
                                    # Escapar comillas simples internas
                                    escaped_content = inner_content.replace("'", "''")
                                    fixed_parts.append(f"'{escaped_content}'")
                                    line_was_modified = True
                                else:
                                    # Ya está bien escapado o no tiene comillas internas
                                    fixed_parts.append(part)
                            else:
                                # No tiene comillas externas
                                if "'" in part:
                                    # Tiene comillas internas, escaparlas y agregar comillas externas
                                    escaped_part = part.replace("'", "''")
                                    fixed_parts.append(f"'{escaped_part}'")
                                    line_was_modified = True
                                else:
                                    # Sin comillas internas, agregar comillas externas
                                    fixed_parts.append(f"'{part}'")

                        if line_was_modified:
                            fixed_count += 1

                        # Reconstruir la línea
                        line = "\t".join(fixed_parts) + "\n"

                    outfile.write(line)

                    # Progreso cada 10,000 líneas
                    if line_count % 10000 == 0:
                        print(
                            f"Procesadas {line_count:,} líneas, arregladas {fixed_count:,}"
                        )

                print(f"\n✓ Completado!")
                print(f"Total líneas procesadas: {line_count:,}")
                print(f"Líneas arregladas: {fixed_count:,}")

        return True

    except Exception as e:
        print(f"Error procesando el archivo: {e}")
        return False


def main():
    """Función principal del script"""
    if len(sys.argv) < 2:
        print("Uso: python fix_copy_quotes.py <archivo_copy_entrada> [archivo_salida]")
        print(
            "\nEste script está especializado para archivos SQL formato COPY FROM STDIN"
        )
        print("\nEjemplo:")
        print("  python fix_copy_quotes.py apollo_part_98_copy_statement.sql")
        print(
            "  python fix_copy_quotes.py apollo_part_98_copy_statement.sql apollo_fixed.sql"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = fix_copy_quotes(input_file, output_file)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
