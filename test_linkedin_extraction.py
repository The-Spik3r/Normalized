#!/usr/bin/env python3
"""
Script de prueba para extraer nombres desde URLs de LinkedIn
"""

import re


def extract_name_from_linkedin_url(url: str) -> str:
    """
    Extrae el nombre de una URL de LinkedIn

    Args:
        url: URL de LinkedIn (ej: linkedin.com/in/john-doe-12345)

    Returns:
        Nombre extraído y formateado (ej: "john doe")
    """
    if not url:
        return None

    try:
        url = str(url).strip()

        # Buscar el patrón /in/ en la URL
        if "/in/" in url:
            # Extraer la parte después de /in/
            parts = url.split("/in/")
            if len(parts) >= 2:
                profile_slug = parts[1]

                # Remover cualquier cosa después de otro /
                profile_slug = profile_slug.split("/")[0]

                # Remover IDs al final (pueden ser solo números o mezcla de números y letras)
                # Ejemplos: -12345, -49020416, -88764a50, -ba555320
                profile_slug = re.sub(r'-[a-z0-9]+$', '', profile_slug)

                # Reemplazar guiones por espacios
                name = profile_slug.replace("-", " ")

                # Limpiar espacios múltiples
                name = " ".join(name.split())

                return name.strip() if name else None

        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    # URLs de prueba (incluyendo casos problemáticos encontrados)
    test_urls = [
        "linkedin.com/in/eva-borneke-49020416",
        "linkedin.com/in/nick-neuland-88764a50",  # ID mixto (letras+números)
        "linkedin.com/in/leslie-pagnotta-74125855",  # Solo números
        "linkedin.com/in/don-hipler-ba555320",  # ID mixto
        "linkedin.com/in/john-doe-12345",
        "https://www.linkedin.com/in/jane-smith-789/",
        "linkedin.com/in/jose-garcia",
        "linkedin.com/in/maria-rodriguez-98765",
        "",
        None,
    ]

    print("=" * 80)
    print("TEST DE EXTRACCIÓN DE NOMBRES DESDE URLs DE LINKEDIN")
    print("=" * 80)
    print()

    for url in test_urls:
        result = extract_name_from_linkedin_url(url)
        print(f"URL:    {url or '[vacío]'}")
        print(f"Nombre: {result or '[N/A]'}")
        print("-" * 80)
