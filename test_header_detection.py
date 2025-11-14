#!/usr/bin/env python3
"""
Script de prueba para verificar la detección de header en CSV
"""

import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def detect_header_test(csv_path: str) -> int | None:
    """
    Detecta si un CSV tiene header.
    Versión de prueba con output detallado.
    """
    try:
        with open(csv_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            first_line = f.readline().strip()

        print("=" * 80)
        print("TEST DE DETECCIÓN DE HEADER")
        print("=" * 80)
        print(f"\nArchivo: {csv_path}")
        print(f"\nPrimera línea completa:\n{first_line[:500]}\n")

        # Limpiar posible BOM o espacios
        first_line = first_line.lstrip('\ufeff').strip()

        # Heurística mejorada
        indicators_of_data = [
            "@",           # Email
            "http://",     # URL
            "https://",    # URL
            ".com",        # Dominio
            ".net",        # Dominio
            ".org",        # Dominio
            "linkedin.com", # LinkedIn específico
            "/in/",        # LinkedIn profile path
            "www.",        # URL
        ]

        first_line_lower = first_line.lower()

        # Verificar cada indicador
        print("Verificando indicadores de datos:")
        matches = 0
        for indicator in indicators_of_data:
            found = indicator in first_line_lower
            if found:
                matches += 1
                print(f"  ✓ '{indicator}' encontrado")
            else:
                print(f"  ✗ '{indicator}' no encontrado")

        print(f"\nTotal de indicadores encontrados: {matches}")

        # Decisión
        if matches > 0:
            print("\n🎯 RESULTADO: CSV SIN HEADER (primera fila contiene datos)")
            print("   → Se usará header=None en pd.read_csv()")
            return None
        else:
            print("\n🎯 RESULTADO: CSV CON HEADER (primera fila son nombres de columnas)")
            print("   → Se usará header=0 en pd.read_csv()")
            return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python test_header_detection.py <ruta_al_csv>")
        print("\nEjemplo: python test_header_detection.py data.csv")
        sys.exit(1)

    csv_file = sys.argv[1]
    result = detect_header_test(csv_file)

    print("\n" + "=" * 80)
    print(f"Valor retornado: {result}")
    print("=" * 80)
