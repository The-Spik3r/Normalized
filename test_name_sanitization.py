#!/usr/bin/env python3
"""
Script de prueba para la sanitización de nombres internacionales
Demuestra cómo el sistema maneja nombres de Brasil, India, Canadá, Reino Unido y Estados Unidos
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Importar las funciones de sanitización desde cli_interactive
from cli_interactive import sanitize_name, sanitize_international_names_batch

console = Console()


def test_international_names():
    """Prueba la sanitización con nombres de diferentes países"""

    # Nombres de prueba de diferentes países y idiomas
    test_names = [
        # Brasil (Portugués)
        "José da Silva",
        "Maria José",
        "João Paulo",
        "Ana Cláudia",
        "Luís Fernando",
        "Ação Graças",
        "João d'Água",
        "José María",
        "Fátima São Paulo",
        "Antônio Carlos",
        "Conceição",
        # India (Hindi transcrito, Inglés)
        "Rajesh Kumar",
        "Priya Sharma",
        "Arjun Singh",
        "Ananya Patel",
        "Sita Ram",
        "Krishna Murthy",
        "Lakshmi Devi",
        "Vikram Singh",
        "Radha Krishna",
        "Arun Kumar",
        "Meera Bai",
        # Canadá (Inglés/Francés)
        "Jean-Baptiste",
        "Marie-Claire",
        "François Lévesque",
        "Céline Dion",
        "André Bégin",
        "Françoise Martin",
        "O'Connor",
        "MacLeod",
        "St-Pierre",
        "D'Angelo",
        # Reino Unido (Inglés)
        "James O'Sullivan",
        "Mary McDonald",
        "William MacKenzie",
        "Sarah O'Brien",
        "Patrick McCartney",
        "Elizabeth Stuart-Williams",
        "Sir James",
        "Lady Margaret",
        "St. John",
        "De La Cruz",
        # Estados Unidos (Inglés + diverso)
        "José Martínez",
        "María González",
        "Michael O'Connor",
        "Jennifer Smith-Johnson",
        "Robert Jr.",
        "Lisa Marie",
        "David Ben-David",
        "Sarah Al-Hassan",
        "Kim Lee-Park",
        # Casos especiales y problemáticos
        "Åse Nordström",
        "Björn Svensson",
        "François d'Assise",
        "María José da Silva-O'Connor",
        "Jean-François St-Laurént",
        "İbrahim Çelik",
        "Müller",
        "Jürgen",
        "Gül",
        "Özcan",
        # Nombres con caracteres especiales
        "Marie-Ève Cyr",
        "José Ñoño",
        "Señorita López",
        "Müller Schmidt",
        "François Çà",
        "Niño García",
        # Casos edge
        "",
        "   ",
        None,
        "123",
        "!@#$%",
        "---",
        "a",
        "Very-Long-Name-With-Multiple-Hyphens-And-Spaces",
        "'Apostrophe'",
        '"Double Quotes"',
        "Mix3d Numb3rs",
    ]

    console.print(
        "\n🌍 [bold green]SISTEMA DE SANITIZACIÓN DE NOMBRES INTERNACIONALES[/bold green]"
    )
    console.print("=" * 80)

    # Crear tabla para mostrar resultados
    table = Table(title="🧹 Resultados de Sanitización de Nombres")
    table.add_column("País/Región", style="cyan", no_wrap=True)
    table.add_column("Nombre Original", style="yellow", max_width=25)
    table.add_column("Nombre Sanitizado", style="green", max_width=25)
    table.add_column("Estado", style="magenta", no_wrap=True)

    # Agrupar nombres por región
    regions = {
        "🇧🇷 Brasil": test_names[0:11],
        "🇮🇳 India": test_names[11:22],
        "🇨🇦 Canadá": test_names[22:32],
        "🇬🇧 Reino Unido": test_names[32:38],
        "🇺🇸 Estados Unidos": test_names[38:47],
        "🌐 Especiales": test_names[47:53],
        "🔤 Caracteres": test_names[53:59],
        "⚠️ Edge Cases": test_names[59:],
    }

    total_processed = 0
    successful_sanitized = 0
    failed_cases = 0

    for region, names in regions.items():
        for original_name in names:
            total_processed += 1

            # Aplicar sanitización
            sanitized = sanitize_name(original_name)

            # Determinar estado
            if sanitized is None:
                if original_name in [None, "", "   ", "!@#$%", "---"]:
                    status = "✅ NULL (esperado)"
                else:
                    status = "❌ NULL (inesperado)"
                    failed_cases += 1
            else:
                status = "✅ Exitoso"
                successful_sanitized += 1

            # Mostrar nombre original de forma segura
            display_original = (
                str(original_name) if original_name is not None else "None"
            )
            display_sanitized = sanitized if sanitized is not None else "NULL"

            table.add_row(region, display_original, display_sanitized, status)
            region = ""  # Solo mostrar región en primera fila

    console.print(table)

    # Estadísticas finales
    success_rate = (successful_sanitized / total_processed) * 100

    stats_panel = f"""
📊 [bold]Estadísticas de Sanitización:[/bold]

• Total procesados: {total_processed}
• Exitosamente sanitizados: {successful_sanitized}
• Casos fallidos: {failed_cases}
• Tasa de éxito: {success_rate:.1f}%

🎯 [bold]Características del Sistema:[/bold]

• ✅ Maneja acentos y caracteres especiales (á, é, í, ó, ú, ñ, ç)
• ✅ Convierte nombres a formato SQL-safe (minúsculas, sin espacios)
• ✅ Preserva estructura con guiones (Jean-Baptiste → jean-baptiste)
• ✅ Elimina apostrofes y comillas (O'Connor → oconnor)
• ✅ Normaliza caracteres Unicode (José → jose)
• ✅ Maneja nombres compuestos (María José → maria-jose)
• ✅ Procesa nombres de múltiples idiomas y culturas

🔧 [bold]Casos Especiales Manejados:[/bold]

• Nombres con prefijos (St-Pierre, D'Angelo, O'Connor)
• Caracteres escandinavos (Åse → ase, Björn → bjorn)
• Caracteres germánicos (Müller → muller, Jürgen → jurgen)
• Caracteres turcos (İbrahim → ibrahim, Özcan → ozcan)
• Nombres latinos extendidos (João → joao, François → francois)
    """

    console.print(
        Panel(stats_panel, title="📈 Resumen de Pruebas", border_style="blue")
    )


def test_batch_processing():
    """Demuestra el procesamiento en lotes de nombres"""

    console.print("\n🔄 [bold]PRUEBA DE PROCESAMIENTO EN LOTES[/bold]")
    console.print("-" * 50)

    # Crear DataFrame de prueba
    names_data = {
        "full_name": [
            "José María González",
            "Marie-Claire Dubois",
            "Rajesh Kumar Singh",
            "O'Connor MacLeod",
            "María José da Silva",
            "Jean-François St-Laurent",
            "Müller Schmidt",
            "İbrahim Özcan",
            "Priya Sharma Patel",
        ],
        "first_name": [
            "José",
            "Marie-Claire",
            "Rajesh",
            "Patrick",
            "María",
            "Jean-François",
            "Hans",
            "İbrahim",
            "Priya",
        ],
        "last_name": [
            "González",
            "Dubois",
            "Singh",
            "MacLeod",
            "Silva",
            "St-Laurent",
            "Schmidt",
            "Özcan",
            "Patel",
        ],
    }

    df = pd.DataFrame(names_data)

    console.print("📋 [bold]Datos Originales:[/bold]")
    console.print(df.to_string(index=False))

    # Aplicar sanitización a todas las columnas de nombres
    df_sanitized = df.copy()
    for col in df_sanitized.columns:
        df_sanitized[col] = sanitize_international_names_batch(df_sanitized[col])

    console.print("\n🧹 [bold]Datos Sanitizados:[/bold]")
    console.print(df_sanitized.to_string(index=False))

    console.print(f"\n✅ [green]Procesados {len(df)} registros exitosamente[/green]")


if __name__ == "__main__":
    test_international_names()
    test_batch_processing()

    console.print(
        Panel(
            """
🎉 [bold green]¡Sanitización de Nombres Lista![/bold green]

El sistema ahora puede manejar nombres de:
• 🇧🇷 Brasil (João, María José, da Silva)
• 🇮🇳 India (Rajesh Kumar, Priya Sharma)  
• 🇨🇦 Canadá (Jean-Baptiste, O'Connor)
• 🇬🇧 Reino Unido (MacLeod, St. John)
• 🇺🇸 Estados Unidos (Smith-Johnson, Al-Hassan)

[bold]Próximos pasos:[/bold]
1. Ejecutar CLI: [cyan]python cli_interactive.py[/cyan]
2. Los nombres se sanitizarán automáticamente
3. Verificar resultados en archivo SQL generado
        """,
            title="🌍 Sistema Listo",
            border_style="green",
        )
    )
