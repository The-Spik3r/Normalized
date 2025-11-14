#!/usr/bin/env python3
"""
CLI Interactivo para CSV to SQL Converter
Con animaciones y opciones de personalización completa
"""

import click
import inquirer
import pandas as pd
import os
import re
import time
import logging
import unicodedata
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.prompt import Prompt, Confirm
from typing import Dict, List
from datetime import datetime

from csv_to_sql import CSVToSQLConverter

console = Console()

# Configurar logging para debug
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Importar funciones de reparación SQL
try:
    from sql_repair_fixed import (
        parse_create_table,
        interactive_edit,
        build_create_table_sql,
        extract_insert_statements,
        try_generate_inserts_from_csv,
        create_sqlite_from_sql,
        ask_sqlite_processing_option,
    )

    SQL_REPAIR_AVAILABLE = True
except ImportError:
    SQL_REPAIR_AVAILABLE = False


def detect_header(csv_path: str) -> int | None:
    """
    Detecta si un CSV tiene header.

    Regla simple pero efectiva:
    - Si la primera fila contiene '@', 'http', '.com', es un dato → header=None.
    - Si la primera fila parece texto o nombres, se asume header=0.

    Args:
        csv_path: Ruta al archivo CSV

    Returns:
        None si no hay header, 0 si hay header
    """
    try:
        with open(csv_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            first_line = f.readline().strip()

        # Log para debug
        logging.info(f"Primera línea del CSV (primeros 200 chars): {first_line[:200]}")

        # Limpiar posible BOM o espacios
        first_line = first_line.lstrip('\ufeff').strip()

        # Heurística mejorada para detectar si el primer campo es dato o no
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

        # Contar cuántos indicadores encontramos
        matches = sum(1 for indicator in indicators_of_data if indicator in first_line_lower)

        logging.info(f"Indicadores de datos encontrados: {matches}")

        # Si encontramos al menos un indicador fuerte, es un dato (no header)
        if matches > 0:
            logging.info("CSV sin header detectado (contiene indicadores de datos)")
            console.print("[cyan]ℹ️  Detectado: CSV sin header. Los nombres de columnas se generarán automáticamente.[/cyan]")
            return None  # No hay header

        logging.info("CSV con header detectado (primera fila parece ser nombres de columnas)")
        return 0  # Sí hay header

    except Exception as e:
        logging.warning(f"Error detectando header, asumiendo header=0: {e}")
        return 0  # Default a header presente si hay error


def sanitize_name(name: str) -> str:
    """
    Sanitiza nombres para manejo internacional (Brasil, India, Canadá, Reino Unido, Estados Unidos)

    Funcionalidades:
    - Convierte a minúsculas
    - Normaliza caracteres Unicode (acentos, diéresis, etc.)
    - Maneja caracteres especiales de múltiples idiomas
    - Preserva guiones y espacios como separadores válidos
    - Elimina caracteres problemáticos para SQL
    """
    if pd.isna(name) or name is None:
        return None

    # Convertir a string y strip
    name = str(name).strip()
    if not name:
        return None

    # Convertir a minúsculas
    name = name.lower()

    # Normalizar caracteres Unicode (NFD = Normalization Form Decomposed)
    # Esto separa caracteres como á en a + ´
    normalized = unicodedata.normalize("NFD", name)

    # Eliminar marcas diacríticas (acentos, tildes, etc.) pero mantener caracteres base
    ascii_name = "".join(
        char
        for char in normalized
        if unicodedata.category(char) != "Mn"  # 'Mn' = Nonspacing_Mark (acentos)
    )

    # Reemplazar caracteres especiales comunes por sus equivalentes ASCII
    replacements = {
        # Caracteres latinos extendidos
        "ß": "ss",  # Alemán
        "æ": "ae",  # Danés, Noruego
        "ø": "o",  # Danés, Noruego
        "å": "a",  # Escandinavo
        "ñ": "n",  # Español
        "ç": "c",  # Francés, Portugués
        "œ": "oe",  # Francés
        # Caracteres de puntuación que pueden aparecer en nombres
        "'": "",  # Apostrofe (O'Connor -> oconnor)
        "`": "",  # Acento grave
        "´": "",  # Acento agudo
        "^": "",  # Circunflejo
        "~": "",  # Tilde
        '"': "",  # Comillas dobles
        # Caracteres especiales de nombres internacionales
        "ł": "l",  # Polaco
        "đ": "d",  # Vietnamita, Serbio
        "ħ": "h",  # Maltés
        "ŧ": "t",  # Sami
        # Espacios y separadores -> guiones
        " ": "-",  # Espacios a guiones
        "_": "-",  # Underscores a guiones
        ".": "-",  # Puntos a guiones
        "/": "-",  # Barras a guiones
        "\\": "-",  # Backslashes a guiones
    }

    # Aplicar reemplazos
    for original, replacement in replacements.items():
        ascii_name = ascii_name.replace(original, replacement)

    # Eliminar caracteres que no sean letras, números o guiones
    # Esto maneja caracteres de otros alfabetos (cirílico, árabe, hindi, etc.)
    sanitized = re.sub(r"[^a-z0-9\-]", "", ascii_name)

    # Limpiar múltiples guiones consecutivos
    sanitized = re.sub(r"-+", "-", sanitized)

    # Eliminar guiones al inicio y final
    sanitized = sanitized.strip("-")

    # Si después de todo el procesamiento el nombre está vacío, retornar None
    if not sanitized:
        return None

    return sanitized


def sanitize_international_names_batch(names_series: pd.Series) -> pd.Series:
    """
    Sanitiza una serie de nombres de forma eficiente

    Args:
        names_series: Serie de pandas con nombres a sanitizar

    Returns:
        Serie de pandas con nombres sanitizados
    """
    return names_series.apply(sanitize_name)


def extract_name_from_linkedin_url(url: str) -> str:
    """
    Extrae el nombre de una URL de LinkedIn

    Args:
        url: URL de LinkedIn (ej: linkedin.com/in/john-doe-12345)

    Returns:
        Nombre extraído y formateado (ej: "john doe")
    """
    if pd.isna(url) or not url:
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
                # Patrón: guion seguido de números/letras (que parecen IDs) al final
                import re
                profile_slug = re.sub(r'-[a-z0-9]+$', '', profile_slug)

                # Reemplazar guiones por espacios
                name = profile_slug.replace("-", " ")

                # Limpiar espacios múltiples
                name = " ".join(name.split())

                return name.strip() if name else None

        return None

    except Exception as e:
        logging.warning(f"Error extrayendo nombre de URL {url}: {e}")
        return None


def extract_names_from_linkedin_batch(urls_series: pd.Series) -> pd.Series:
    """
    Extrae nombres desde una serie de URLs de LinkedIn

    Args:
        urls_series: Serie de pandas con URLs de LinkedIn

    Returns:
        Serie de pandas con nombres extraídos
    """
    return urls_series.apply(extract_name_from_linkedin_url)


def sql_repair_mode():
    """Modo de reparación de SQL"""
    if not SQL_REPAIR_AVAILABLE:
        console.print("[red]❌ Módulo de reparación SQL no disponible[/red]")
        return False

    console.clear()
    console.print(
        Panel(
            "[bold]🛠️ REPARACIÓN DE ARCHIVOS SQL[/bold]\n\n"
            "Esta herramienta te permite:\n"
            "• 📋 Parsear un CREATE TABLE existente\n"
            "• ❌ Eliminar columnas no deseadas\n"
            "• ✏️ Renombrar columnas y cambiar tipos\n"
            "• 🏷️ Cambiar nombre de la tabla\n"
            "• 📄 Generar SQL corregido\n"
            "• 📊 (Opcional) Añadir INSERTs desde CSV\n",
            title="🔧 SQL Repair Tool",
            border_style="blue",
        )
    )

    # Seleccionar archivo SQL
    sql_path = Prompt.ask("📁 Ruta del archivo SQL a reparar")

    if not os.path.exists(sql_path):
        console.print(f"[red]❌ No existe el archivo: {sql_path}[/red]")
        return False

    try:
        # Leer archivo SQL
        with open(sql_path, "r", encoding="utf-8", errors="ignore") as f:
            sql_text = f.read()

        # Parsear CREATE TABLE
        table_name, columns = parse_create_table(sql_text)

        # Edición interactiva
        new_table_name, edited_columns, _ = interactive_edit(table_name, columns)

        # Generar SQL corregido
        corrected_sql = build_create_table_sql(new_table_name, edited_columns)

        # Escribir archivo corregido
        base = os.path.splitext(os.path.basename(sql_path))[0]
        out_file = os.path.join(os.path.dirname(sql_path), f"{base}_corrected.sql")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write("-- Archivo SQL corregido/generado por CSV to SQL Converter CLI\n")
            f.write(f"-- Fuente: {sql_path}\n")
            f.write(
                f"-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write(corrected_sql)

            # Siempre buscar y generar INSERTs desde VALUES existentes o INSERT statements
            console.print(
                "[cyan]🔍 Buscando INSERT statements y VALUES en el archivo original...[/cyan]"
            )
            column_names = [col[0] for col in edited_columns]
            column_types = [col[1] for col in edited_columns]
            insert_sql = extract_insert_statements(
                sql_text, new_table_name, column_names, 0, None, column_types
            )

            if insert_sql.strip():  # Solo escribir si encontramos INSERT statements
                f.write(
                    "\n-- INSERT statements (existentes y extraídos desde VALUES)\n"
                )
                f.write(insert_sql)
                console.print(
                    "[green]✅ INSERT statements incluidos en el archivo[/green]"
                )
            else:
                console.print(
                    "[yellow]⚠️ No se encontraron INSERT statements ni VALUES en el archivo[/yellow]"
                )

        # Mostrar estadísticas del archivo generado
        file_size = os.path.getsize(out_file) / (1024 * 1024)  # MB
        console.print(
            Panel(
                f"✅ SQL corregido escrito en: [bold]{out_file}[/bold]\n"
                f"📊 Tamaño del archivo: [cyan]{file_size:.2f} MB[/cyan]",
                title="🎉 Completado",
                border_style="green",
            )
        )

        # Preguntar por INSERTs desde CSV solo si no se encontraron VALUES
        if not insert_sql.strip() and Confirm.ask(
            "📄 No se encontraron VALUES. ¿Deseas generar INSERTs desde un CSV?",
            default=False,
        ):
            csv_path = Prompt.ask("� Ruta del archivo CSV")
            if os.path.exists(csv_path):
                column_names = [col[0] for col in edited_columns]
                success = try_generate_inserts_from_csv(
                    csv_path, column_names, out_file, new_table_name
                )
                if success:
                    console.print(
                        "[green]✅ INSERTs desde CSV generados exitosamente[/green]"
                    )
                else:
                    console.print(
                        "[yellow]⚠️ Hubo problemas generando los INSERTs desde CSV[/yellow]"
                    )
            else:
                console.print(f"[red]❌ No se encontró el CSV: {csv_path}[/red]")

        # Preguntar si quiere crear base de datos SQLite
        console.print("\n" + "=" * 80)
        console.print(
            Panel(
                "¿Deseas crear una base de datos SQLite y ejecutar las migraciones?\n\n"
                "🗄️ Esto creará un archivo .db listo para usar con todos los datos importados.\n"
                "📊 Ideal para consultas, análisis o integración con aplicaciones.",
                title="🗄️ Crear Base de Datos SQLite",
                border_style="cyan",
            )
        )

        if Confirm.ask("¿Crear base de datos SQLite con los datos?", default=True):
            # Preguntar cuántos registros procesar para SQLite
            console.print(
                Panel(
                    "Selecciona cuántos registros migrar a la base de datos SQLite.\n"
                    "💡 Para archivos grandes, se recomienda empezar con una muestra.",
                    title="📊 Configurar Migración SQLite",
                    border_style="blue",
                )
            )

            max_inserts = ask_sqlite_processing_option()

            sqlite_file = create_sqlite_from_sql(out_file, new_table_name, max_inserts)
            if sqlite_file:
                console.print("\n")
                console.print(
                    Panel(
                        f"🎉 ¡Base de datos SQLite creada exitosamente!\n\n"
                        f"📍 Ubicación: [bold]{sqlite_file}[/bold]\n"
                        f"💡 Puedes usarla con: [dim]sqlite3 {os.path.basename(sqlite_file)}[/dim]",
                        title="✅ Base de Datos Lista",
                        border_style="green",
                    )
                )
            else:
                console.print("[red]❌ No se pudo crear la base de datos SQLite[/red]")

        console.print("\n🎉 ¡Reparación completada exitosamente!")
        return True

    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        return False


class InteractiveCSVConverter:
    def __init__(self):
        self.csv_file = None
        self.table_name = None
        self.column_mapping = {}
        self.type_mapping = {}
        self.sample_df = None
        self.excluded_columns = []
        self.linkedin_columns_map = {}  # Mapeo de columna LinkedIn → columna de nombre extraído

    def show_welcome(self):
        """Muestra la pantalla de bienvenida para conversión CSV"""
        console.print(
            Panel(
                "[bold]� CONVERSIÓN CSV A SQL[/bold]\n\n"
                "Este flujo te permitirá:\n"
                "• 📁 Seleccionar archivo CSV\n"
                "• 🔍 Analizar estructura automáticamente\n"
                "• 🏷️ Configurar nombre de tabla\n"
                "• ⚙️ Personalizar columnas y tipos\n"
                "• 🧹 Sanitización automática de nombres\n"
                "• 💾 Generar SQL con INSERT statements\n",
                title="� CSV Converter",
                border_style="cyan",
            )
        )

        if not Confirm.ask("¿Comenzamos la conversión de CSV a SQL?", default=True):
            return False

        return True

    def select_csv_file(self) -> bool:
        """Selecciona el archivo CSV"""
        console.print("\n📁 [bold]SELECCIÓN DE ARCHIVO CSV[/bold]", style="blue")
        console.print("─" * 50)

        # Buscar archivos CSV en el directorio actual y padre
        csv_files = []

        # Directorio actual
        for file in os.listdir("."):
            if file.endswith(".csv"):
                csv_files.append(f"./{file}")

        # Directorio padre
        parent_dir = "../"
        if os.path.exists(parent_dir):
            for file in os.listdir(parent_dir):
                if file.endswith(".csv"):
                    csv_files.append(f"../{file}")

        if csv_files:
            console.print("📋 Archivos CSV encontrados:")
            for i, file in enumerate(csv_files, 1):
                size = os.path.getsize(file) / 1024 / 1024  # MB
                console.print(f"  {i}. [cyan]{file}[/cyan] ({size:.1f} MB)")

            csv_files.append("🔍 Especificar ruta manualmente")

            questions = [
                inquirer.List(
                    "csv_file",
                    message="Selecciona el archivo CSV",
                    choices=csv_files,
                    carousel=True,
                )
            ]

            answers = inquirer.prompt(questions)

            if answers["csv_file"] == "🔍 Especificar ruta manualmente":
                self.csv_file = Prompt.ask("📝 Ingresa la ruta del archivo CSV")
            else:
                self.csv_file = answers["csv_file"]
        else:
            console.print("⚠️  No se encontraron archivos CSV automáticamente")
            self.csv_file = Prompt.ask("📝 Ingresa la ruta del archivo CSV")

        # Verificar que el archivo existe
        if not os.path.exists(self.csv_file):
            console.print(
                f"❌ [red]Error: No se encontró el archivo {self.csv_file}[/red]"
            )
            return False

        # Mostrar información del archivo
        file_size = os.path.getsize(self.csv_file) / 1024 / 1024
        console.print(
            f"\n✅ [green]Archivo seleccionado:[/green] [cyan]{self.csv_file}[/cyan]"
        )
        console.print(f"📏 [bold]Tamaño:[/bold] {file_size:.2f} MB")

        return True

    def analyze_csv_structure(self) -> bool:
        """Analiza la estructura del CSV y muestra preview"""
        console.print("\n🔍 [bold]ANÁLISIS DE ESTRUCTURA[/bold]", style="blue")
        console.print("─" * 50)

        with console.status("[bold green]Analizando archivo CSV..."):
            try:
                # Detectar si el CSV tiene header
                header_option = detect_header(self.csv_file)

                # Leer muestra del archivo
                self.sample_df = pd.read_csv(
                    self.csv_file,
                    nrows=1000,
                    header=header_option,
                    on_bad_lines="skip",
                    dtype=str
                )

                # Si no hay header, Pandas asigna nombres numéricos (0, 1, 2...)
                # Los convertimos a nombres descriptivos
                if header_option is None:
                    new_columns = [f"col_{i}" for i in range(len(self.sample_df.columns))]
                    self.sample_df.columns = new_columns

                time.sleep(0.5)  # Para mostrar la animación

            except Exception as e:
                console.print(f"❌ [red]Error leyendo el archivo: {e}[/red]")
                return False

        # Mostrar información básica
        info_table = Table(title="📊 Información del Archivo")
        info_table.add_column("Propiedad", style="cyan")
        info_table.add_column("Valor", style="green")

        info_table.add_row("Columnas", str(len(self.sample_df.columns)))
        info_table.add_row("Filas analizadas", "1,000 (muestra)")
        info_table.add_row("Tipos únicos", str(self.sample_df.dtypes.nunique()))

        console.print(info_table)

        # Mostrar preview de datos
        console.print("\n📋 [bold]Vista Previa de Datos:[/bold]")

        preview_table = Table(show_lines=True)

        # Agregar columnas (limitar a 5 para no saturar)
        display_cols = list(self.sample_df.columns)[:5]
        for col in display_cols:
            preview_table.add_column(str(col)[:20], style="cyan")

        # Agregar filas (primeras 3)
        for i in range(min(3, len(self.sample_df))):
            row_data = []
            for col in display_cols:
                value = str(self.sample_df.iloc[i][col])
                # Truncar valores largos
                if len(value) > 20:
                    value = value[:17] + "..."
                row_data.append(value)
            preview_table.add_row(*row_data)

        console.print(preview_table)

        if len(self.sample_df.columns) > 5:
            console.print(f"... y {len(self.sample_df.columns) - 5} columnas más")

        # Detectar si hay columnas de LinkedIn y ofrecer extraer nombres
        self._detect_and_offer_linkedin_extraction()

        return True

    def _detect_and_offer_linkedin_extraction(self):
        """Detecta columnas de LinkedIn y ofrece extraer nombres"""
        linkedin_columns = []

        # Buscar columnas que contengan URLs de LinkedIn
        for col in self.sample_df.columns:
            # Revisar las primeras filas de cada columna
            sample_values = self.sample_df[col].dropna().head(10).astype(str)
            if any("linkedin.com/in/" in str(val).lower() for val in sample_values):
                linkedin_columns.append(col)

        if linkedin_columns:
            console.print(
                f"\n[bold yellow]🔍 Detecté {len(linkedin_columns)} columna(s) con URLs de LinkedIn:[/bold yellow]"
            )
            for col in linkedin_columns:
                console.print(f"   • {col}")

            console.print(
                "\n[cyan]💡 Puedo extraer los NOMBRES desde estas URLs automáticamente.[/cyan]"
            )
            console.print(
                "[dim]Ejemplo: 'linkedin.com/in/john-doe-12345' → 'john doe'[/dim]\n"
            )

            if Confirm.ask(
                "¿Deseas agregar columna(s) con nombres extraídos de LinkedIn?",
                default=True,
            ):
                for linkedin_col in linkedin_columns:
                    # Generar nombre para la nueva columna
                    new_col_name = f"{linkedin_col}_name"

                    # Guardar el mapeo para usarlo durante la conversión completa
                    self.linkedin_columns_map[linkedin_col] = new_col_name

                    # Extraer nombres en la muestra
                    with console.status(
                        f"[bold green]Extrayendo nombres desde {linkedin_col}..."
                    ):
                        self.sample_df[new_col_name] = extract_names_from_linkedin_batch(
                            self.sample_df[linkedin_col]
                        )
                        time.sleep(0.3)

                    # Mostrar algunos ejemplos
                    console.print(
                        f"\n[green]✅ Columna '{new_col_name}' creada exitosamente[/green]"
                    )
                    console.print("[bold]Ejemplos de nombres extraídos:[/bold]")

                    examples_table = Table(show_header=True, box=None)
                    examples_table.add_column("URL Original", style="yellow", width=40)
                    examples_table.add_column("Nombre Extraído", style="green")

                    for i in range(min(3, len(self.sample_df))):
                        url = str(self.sample_df[linkedin_col].iloc[i])[:40] + "..."
                        name = self.sample_df[new_col_name].iloc[i]
                        examples_table.add_row(url, str(name) if name else "[dim]N/A[/dim]")

                    console.print(examples_table)

                console.print(
                    f"\n[bold green]🎉 Se agregaron {len(linkedin_columns)} columna(s) de nombres![/bold green]"
                )
            else:
                console.print(
                    "[dim]No se agregarán columnas de nombres. Continuando...[/dim]"
                )

    def count_total_rows(self) -> int:
        """Cuenta el total de filas en el archivo CSV (excluyendo el header)"""
        try:
            with console.status("[bold green]Contando filas totales..."):
                # Contar líneas del archivo (más eficiente que cargar todo el DataFrame)
                with open(self.csv_file, "r", encoding="utf-8") as f:
                    total_lines = sum(1 for line in f)
                # Restar 1 para excluir el header
                return total_lines - 1
        except Exception as e:
            console.print(f"[red]❌ Error al contar filas: {e}[/red]")
            return 0

    def configure_table_name(self) -> bool:
        """Configura el nombre de la tabla"""
        console.print("\n🏷️  [bold]CONFIGURACIÓN DE TABLA[/bold]", style="blue")
        console.print("─" * 50)

        # Generar nombre automático
        filename = os.path.basename(self.csv_file)
        auto_name = re.sub(r"[^a-zA-Z0-9_]", "_", filename.split(".")[0])
        if auto_name[0].isdigit():
            auto_name = "table_" + auto_name
        auto_name = auto_name.lower()

        console.print(f"💡 [bold]Nombre sugerido:[/bold] [yellow]{auto_name}[/yellow]")

        questions = [
            inquirer.List(
                "table_option",
                message="¿Qué deseas hacer con el nombre de la tabla?",
                choices=[
                    f"✅ Usar nombre sugerido: {auto_name}",
                    "✏️  Especificar nombre personalizado",
                    "🎲 Generar nombre aleatorio",
                ],
            )
        ]

        answers = inquirer.prompt(questions)

        if "Usar nombre sugerido" in answers["table_option"]:
            self.table_name = auto_name
        elif "Especificar nombre personalizado" in answers["table_option"]:
            while True:
                custom_name = Prompt.ask("📝 Ingresa el nombre de la tabla")
                # Validar nombre
                if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", custom_name):
                    self.table_name = custom_name.lower()
                    break
                else:
                    console.print(
                        "❌ [red]Nombre inválido. Debe comenzar con letra y contener solo letras, números y guiones bajos.[/red]"
                    )
        else:  # Generar aleatorio
            import random

            random_suffix = random.randint(1000, 9999)
            self.table_name = f"data_table_{random_suffix}"

        console.print(
            f"✅ [green]Nombre de tabla configurado:[/green] [bold cyan]{self.table_name}[/bold cyan]"
        )
        return True

    def _configure_columns_to_exclude(self) -> bool:
        """Permite al usuario seleccionar qué columnas eliminar de la tabla"""
        console.print(
            "\n🗑️  [bold]SELECCIÓN DE COLUMNAS A EXCLUIR[/bold]", style="yellow"
        )
        console.print("─" * 50)
        console.print(
            "💡 [dim]Selecciona las columnas que NO quieres incluir en la tabla SQL[/dim]"
        )
        console.print(
            "💡 [dim]Útil para: IDs autoincrement, timestamps automáticos, columnas calculadas, etc.[/dim]\n"
        )

        # Mostrar preview de las columnas disponibles
        preview_table = Table(title="📋 Columnas Disponibles en el CSV")
        preview_table.add_column("N°", style="cyan", no_wrap=True, width=4)
        preview_table.add_column("Nombre de Columna", style="green", no_wrap=True)
        preview_table.add_column("Tipo Detectado", style="magenta", no_wrap=True)
        preview_table.add_column("Muestra de Datos", style="yellow", max_width=30)

        for i, column in enumerate(self.sample_df.columns, 1):
            detected_type = self._detect_column_type(column)
            # Obtener muestra de datos (primeros 3 valores no-nulos)
            sample_data = self.sample_df[column].dropna().head(3).tolist()
            sample_str = (
                ", ".join([str(x)[:20] for x in sample_data]) if sample_data else "N/A"
            )

            preview_table.add_row(
                str(i),
                str(column),
                detected_type,
                sample_str + ("..." if len(sample_str) > 30 else ""),
            )

        console.print(preview_table)

        # Preguntar si quiere excluir columnas
        questions = [
            inquirer.Confirm(
                "exclude_columns",
                message="¿Deseas excluir alguna columna de la tabla SQL?",
                default=False,
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers["exclude_columns"]:
            console.print(
                "✅ [green]Todas las columnas serán incluidas en la tabla[/green]"
            )
            return True

        # Crear lista de columnas para selección múltiple
        column_choices = []
        for i, column in enumerate(self.sample_df.columns):
            # Detectar casos comunes de columnas que se suelen excluir
            exclude_hints = []
            col_lower = str(column).lower()

            if any(x in col_lower for x in ["id", "key", "pk", "primary"]):
                exclude_hints.append("🔑 ID/Key")
            if any(
                x in col_lower
                for x in ["created", "updated", "modified", "timestamp", "date_created"]
            ):
                exclude_hints.append("📅 Timestamp")
            if any(x in col_lower for x in ["auto", "increment", "serial"]):
                exclude_hints.append("🔢 Auto")
            if any(x in col_lower for x in ["calculated", "computed", "derived"]):
                exclude_hints.append("🧮 Calculado")

            hint_text = f" ({', '.join(exclude_hints)})" if exclude_hints else ""
            column_choices.append(f"{column}{hint_text}")

        # Selección múltiple de columnas a excluir
        questions = [
            inquirer.Checkbox(
                "columns_to_exclude",
                message="Selecciona las columnas que quieres EXCLUIR (usa ESPACIO para marcar, ENTER para confirmar):",
                choices=column_choices,
                default=[],
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return False

        excluded_columns = []
        for selected in answers["columns_to_exclude"]:
            # Extraer el nombre original de la columna (antes de los hints)
            original_name = selected.split(" (")[0] if " (" in selected else selected
            excluded_columns.append(original_name)

        if excluded_columns:
            # Guardar las columnas excluidas para usarlas durante el procesamiento completo
            self.excluded_columns = excluded_columns

            # Actualizar el DataFrame para excluir las columnas seleccionadas
            self.sample_df = self.sample_df.drop(columns=excluded_columns)

            console.print(
                f"\n🗑️ [red]Columnas excluidas:[/red] {', '.join(excluded_columns)}"
            )
            console.print(
                f"✅ [green]Columnas restantes:[/green] {len(self.sample_df.columns)} de {len(self.sample_df.columns) + len(excluded_columns)} originales"
            )

            # Mostrar tabla final
            final_table = Table(title="📋 Columnas Finales para la Tabla SQL")
            final_table.add_column("N°", style="cyan", no_wrap=True)
            final_table.add_column("Columna", style="green", no_wrap=True)
            final_table.add_column("Tipo", style="magenta", no_wrap=True)

            for i, column in enumerate(self.sample_df.columns, 1):
                final_table.add_row(
                    str(i), str(column), self._detect_column_type(column)
                )

            console.print("\n" + "─" * 50)
            console.print(final_table)
        else:
            console.print("✅ [green]No se excluyeron columnas[/green]")

        return True

    def configure_columns(self) -> bool:
        """Configura nombres y tipos de columnas"""
        console.print("\n🏗️  [bold]CONFIGURACIÓN DE COLUMNAS[/bold]", style="blue")
        console.print("─" * 50)

        # Primero preguntar si quiere eliminar columnas
        if not self._configure_columns_to_exclude():
            return False

        # Preguntar nivel de personalización
        questions = [
            inquirer.List(
                "customization_level",
                message="¿Qué nivel de personalización deseas?",
                choices=[
                    "🚀 Rápido - Usar configuración automática",
                    "⚙️  Intermedio - Revisar y ajustar nombres",
                    "🔧 Avanzado - Personalizar todo (nombres y tipos)",
                    "🎯 Experto - Configurar cada columna individualmente",
                ],
            )
        ]

        answers = inquirer.prompt(questions)
        level = answers["customization_level"]

        if "Rápido" in level:
            return self._auto_configure_columns()
        elif "Intermedio" in level:
            return self._intermediate_configure_columns()
        elif "Avanzado" in level:
            return self._advanced_configure_columns()
        else:  # Experto
            return self._expert_configure_columns()

    def _auto_configure_columns(self) -> bool:
        """Configuración automática de columnas"""
        with console.status("[bold green]Configurando columnas automáticamente..."):
            for column in self.sample_df.columns:
                # Limpiar nombre de columna
                clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(column))
                if clean_name[0].isdigit():
                    clean_name = "col_" + clean_name
                self.column_mapping[column] = clean_name.lower()

                # Detectar tipo automáticamente
                self.type_mapping[column] = self._detect_column_type(column)

            time.sleep(1)

        console.print("✅ [green]Configuración automática completada[/green]")
        return True

    def _intermediate_configure_columns(self) -> bool:
        """Configuración intermedia - revisar nombres"""
        console.print("📝 [bold]Revisión de Nombres de Columnas[/bold]")

        for i, column in enumerate(self.sample_df.columns):
            # Generar nombre limpio
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(column))
            if clean_name[0].isdigit():
                clean_name = "col_" + clean_name
            clean_name = clean_name.lower()

            console.print(
                f"\n[cyan]Columna {i + 1}/{len(self.sample_df.columns)}:[/cyan]"
            )
            console.print(f"📋 Original: [yellow]{column}[/yellow]")
            console.print(f"🔧 Sugerido: [green]{clean_name}[/green]")

            # Mostrar muestra de datos
            sample_values = self.sample_df[column].dropna().head(3).tolist()
            console.print(f"📊 Ejemplos: {sample_values}")

            if Confirm.ask(f"¿Usar nombre sugerido '{clean_name}'?", default=True):
                self.column_mapping[column] = clean_name
            else:
                custom_name = Prompt.ask("📝 Ingresa nombre personalizado")
                self.column_mapping[column] = custom_name.lower()

            # Tipo automático
            self.type_mapping[column] = self._detect_column_type(column)

        return True

    def _advanced_configure_columns(self) -> bool:
        """Configuración avanzada - nombres y tipos"""
        console.print("🔧 [bold]Configuración Avanzada de Columnas[/bold]")

        # Crear tabla de configuración
        config_table = Table(title="Configuración de Columnas")
        config_table.add_column("Original", style="yellow")
        config_table.add_column("Nuevo Nombre", style="green")
        config_table.add_column("Tipo SQL", style="cyan")
        config_table.add_column("Ejemplos", style="dim")

        for column in self.sample_df.columns:
            # Configurar nombre
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(column))
            if clean_name[0].isdigit():
                clean_name = "col_" + clean_name
            clean_name = clean_name.lower()

            console.print(f"\n🔧 [bold]Configurando: {column}[/bold]")

            if Confirm.ask(f"¿Usar nombre '{clean_name}'?", default=True):
                new_name = clean_name
            else:
                new_name = Prompt.ask("Nuevo nombre")

            # Configurar tipo
            auto_type = self._detect_column_type(column)
            type_options = [
                "VARCHAR(255)",
                "INT",
                "DECIMAL(10,2)",
                "DATETIME",
                "TEXT",
                "BOOLEAN",
            ]

            questions = [
                inquirer.List(
                    "sql_type",
                    message=f"Tipo SQL para '{new_name}' (detectado: {auto_type})",
                    choices=type_options + [f"✅ Usar detectado: {auto_type}"],
                    default=f"✅ Usar detectado: {auto_type}",
                )
            ]

            answers = inquirer.prompt(questions)

            if "Usar detectado" in answers["sql_type"]:
                sql_type = auto_type
            else:
                sql_type = answers["sql_type"]

            self.column_mapping[column] = new_name
            self.type_mapping[column] = sql_type

            # Mostrar en tabla
            sample_values = str(self.sample_df[column].dropna().head(2).tolist())
            config_table.add_row(
                column[:20], new_name, sql_type, sample_values[:30] + "..."
            )

        console.print(config_table)
        return True

    def _expert_configure_columns(self) -> bool:
        """Configuración experta - control total"""
        console.print("🎯 [bold]Configuración Experta - Control Total[/bold]")

        for i, column in enumerate(self.sample_df.columns):
            console.clear()
            console.print(
                f"🎯 [bold]Columna {i + 1} de {len(self.sample_df.columns)}[/bold]",
                style="blue",
            )
            console.print("=" * 60)

            # Panel con información detallada
            column_info = f"""
📋 [bold]Nombre Original:[/bold] {column}
📊 [bold]Tipo Pandas:[/bold] {self.sample_df[column].dtype}
🔢 [bold]Valores únicos:[/bold] {self.sample_df[column].nunique()}
❓ [bold]Valores nulos:[/bold] {self.sample_df[column].isnull().sum()}
            """

            console.print(
                Panel(column_info, title="Información de Columna", border_style="cyan")
            )

            # Mostrar estadísticas
            if self.sample_df[column].dtype in ["int64", "float64"]:
                stats_table = Table(title="📊 Estadísticas")
                stats_table.add_column("Estadística", style="cyan")
                stats_table.add_column("Valor", style="green")

                stats_table.add_row("Mínimo", str(self.sample_df[column].min()))
                stats_table.add_row("Máximo", str(self.sample_df[column].max()))
                stats_table.add_row("Promedio", f"{self.sample_df[column].mean():.2f}")

                console.print(stats_table)
            else:
                # Mostrar valores más frecuentes
                top_values = self.sample_df[column].value_counts().head(5)
                values_table = Table(title="🔝 Valores Más Frecuentes")
                values_table.add_column("Valor", style="yellow")
                values_table.add_column("Frecuencia", style="green")

                for value, count in top_values.items():
                    value_str = (
                        str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                    )
                    values_table.add_row(value_str, str(count))

                console.print(values_table)

            # Configurar nombre
            console.print("\n🏷️  [bold]Configuración de Nombre:[/bold]")
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(column))
            if clean_name[0].isdigit():
                clean_name = "col_" + clean_name
            clean_name = clean_name.lower()

            new_name = Prompt.ask("Nombre para la columna", default=clean_name)

            # Configurar tipo con opciones avanzadas
            console.print("\n🔧 [bold]Configuración de Tipo SQL:[/bold]")
            auto_type = self._detect_column_type(column)

            type_categories = {
                "📝 Texto": [
                    "VARCHAR(50)",
                    "VARCHAR(255)",
                    "VARCHAR(1000)",
                    "TEXT",
                    "LONGTEXT",
                ],
                "🔢 Numérico": [
                    "INT",
                    "BIGINT",
                    "DECIMAL(10,2)",
                    "DECIMAL(15,4)",
                    "FLOAT",
                    "DOUBLE",
                ],
                "📅 Fecha/Hora": ["DATE", "DATETIME", "TIMESTAMP", "TIME"],
                "🔘 Otros": ["BOOLEAN", "JSON", "BLOB"],
            }

            console.print(f"💡 [bold]Tipo detectado:[/bold] [green]{auto_type}[/green]")

            questions = [
                inquirer.List(
                    "type_category",
                    message="Selecciona categoría de tipo",
                    choices=list(type_categories.keys())
                    + [f"✅ Usar detectado: {auto_type}"],
                )
            ]

            answers = inquirer.prompt(questions)

            if "Usar detectado" in answers["type_category"]:
                sql_type = auto_type
            else:
                category = answers["type_category"]
                questions = [
                    inquirer.List(
                        "sql_type",
                        message=f"Selecciona tipo específico en {category}",
                        choices=type_categories[category] + ["🛠️  Personalizado"],
                    )
                ]

                answers = inquirer.prompt(questions)

                if answers["sql_type"] == "🛠️  Personalizado":
                    sql_type = Prompt.ask("Ingresa tipo SQL personalizado")
                else:
                    sql_type = answers["sql_type"]

            self.column_mapping[column] = new_name
            self.type_mapping[column] = sql_type

            # Confirmar configuración
            console.print(
                f"\n✅ [green]Configurado:[/green] [yellow]{column}[/yellow] → [cyan]{new_name}[/cyan] ([bold]{sql_type}[/bold])"
            )

            if i < len(self.sample_df.columns) - 1:
                if not Confirm.ask(
                    "¿Continuar con la siguiente columna?", default=True
                ):
                    # Configurar resto automáticamente
                    remaining_columns = list(self.sample_df.columns)[i + 1 :]
                    with console.status(
                        "[bold green]Configurando columnas restantes automáticamente..."
                    ):
                        for remaining_col in remaining_columns:
                            clean_name = re.sub(
                                r"[^a-zA-Z0-9_]", "_", str(remaining_col)
                            )
                            if clean_name[0].isdigit():
                                clean_name = "col_" + clean_name
                            self.column_mapping[remaining_col] = clean_name.lower()
                            self.type_mapping[remaining_col] = self._detect_column_type(
                                remaining_col
                            )
                        time.sleep(1)
                    break

        return True

    def _detect_column_type(self, column: str) -> str:
        """Detecta el tipo de datos de una columna"""
        series = self.sample_df[column]

        if series.dtype == "object":
            # Verificar si es fecha
            try:
                pd.to_datetime(series.dropna().iloc[:100])
                return "DATETIME"
            except Exception:
                # Determinar tamaño de VARCHAR
                max_length = series.astype(str).str.len().max()
                if max_length <= 50:
                    return "VARCHAR(50)"
                elif max_length <= 255:
                    return "VARCHAR(255)"
                else:
                    return "TEXT"
        elif series.dtype in ["int64", "int32"]:
            return "INT"
        elif series.dtype in ["float64", "float32"]:
            return "DECIMAL(10,2)"
        elif series.dtype == "bool":
            return "BOOLEAN"
        else:
            return "TEXT"

    def show_configuration_summary(self) -> bool:
        """Muestra resumen de la configuración"""
        console.print("\n📋 [bold]RESUMEN DE CONFIGURACIÓN[/bold]", style="blue")
        console.print("=" * 60)

        # Información general
        info_panel = f"""
📄 [bold]Archivo CSV:[/bold] {self.csv_file}
🏷️  [bold]Nombre de tabla:[/bold] {self.table_name}
🔢 [bold]Total de columnas:[/bold] {len(self.column_mapping)}
        """

        console.print(
            Panel(info_panel, title="Configuración General", border_style="green")
        )

        # Tabla de columnas
        columns_table = Table(title="🏗️  Mapeo de Columnas")
        columns_table.add_column("Original", style="yellow", width=25)
        columns_table.add_column("SQL", style="cyan", width=25)
        columns_table.add_column("Tipo", style="green", width=15)

        for original, new_name in self.column_mapping.items():
            sql_type = self.type_mapping[original]
            # Truncar nombres largos
            orig_display = original[:22] + "..." if len(original) > 25 else original
            new_display = new_name[:22] + "..." if len(new_name) > 25 else new_name
            columns_table.add_row(orig_display, new_display, sql_type)

        console.print(columns_table)

        # Confirmar configuración
        console.print()
        if not Confirm.ask("¿La configuración es correcta?", default=True):
            console.print(
                "🔧 [yellow]Puedes reiniciar el proceso o hacer ajustes manuales[/yellow]"
            )
            return False

        return True

    def perform_conversion(self) -> bool:
        """Realiza la conversión con animación de progreso"""
        console.print("\n🚀 [bold]INICIANDO CONVERSIÓN[/bold]", style="blue")
        console.print("=" * 50)

        # Obtener el total de filas para mostrar en la opción "Archivo completo"
        total_rows = self.count_total_rows()

        # Preguntar cantidad de filas
        questions = [
            inquirer.List(
                "rows_option",
                message="¿Cuántas filas quieres convertir?",
                choices=[
                    "🧪 Muestra pequeña (100 filas)",
                    "📊 Muestra mediana (5,000 filas)",
                    "📈 Muestra grande (50,000 filas)",
                    f"🌍 Archivo completo ({total_rows:,} filas)",
                    "🛠️  Cantidad personalizada",
                ],
            )
        ]

        answers = inquirer.prompt(questions)

        if "pequeña" in answers["rows_option"]:
            max_rows = 100
        elif "mediana" in answers["rows_option"]:
            max_rows = 5000
        elif "grande" in answers["rows_option"]:
            max_rows = 50000
        elif "completo" in answers["rows_option"]:
            max_rows = None
        else:  # personalizada
            max_rows = int(
                Prompt.ask("🔢 Ingresa la cantidad de filas", default="1000")
            )

        # Crear convertidor personalizado
        converter = CustomCSVToSQLConverter(
            self.csv_file,
            self.table_name,
            self.column_mapping,
            self.type_mapping,
            self.excluded_columns,
            self.linkedin_columns_map,
        )

        # Mostrar progreso con animación
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True,
        ) as progress:
            task1 = progress.add_task("[cyan]Iniciando conversión...", total=100)
            time.sleep(0.5)
            progress.update(task1, advance=20)

            task2 = progress.add_task("[yellow]Detectando estructura...", total=100)
            time.sleep(0.8)
            progress.update(task1, advance=30)
            progress.update(task2, advance=50)

            task3 = progress.add_task("[green]Procesando datos...", total=100)

            try:
                start_time = datetime.now()
                sql_file = converter.convert_to_sql(chunk_size=1000, max_rows=max_rows)
                end_time = datetime.now()

                progress.update(task1, completed=100)
                progress.update(task2, completed=100)
                progress.update(task3, completed=100)

            except Exception as e:
                console.print(f"\n❌ [red]Error durante la conversión: {e}[/red]")
                return False

        # Mostrar resultados
        duration = (end_time - start_time).total_seconds()
        sql_size = os.path.getsize(sql_file) / 1024 / 1024  # MB
        processed_rows = max_rows or "Todas"

        results_panel = f"""
✅ [bold green]CONVERSIÓN EXITOSA[/bold green]

📄 [bold]Archivo SQL:[/bold] {sql_file}
🗂️  [bold]Tabla SQL:[/bold] {self.table_name}
📊 [bold]Filas procesadas:[/bold] {processed_rows}
📏 [bold]Tamaño SQL:[/bold] {sql_size:.2f} MB
⏱️  [bold]Tiempo:[/bold] {duration:.2f} segundos
⚡ [bold]Velocidad:[/bold] {(max_rows or 1000) / duration:.0f} filas/segundo
        """

        console.print(Panel(results_panel, title="🎉 Resultados", border_style="green"))

        # Mostrar preview del SQL
        if Confirm.ask("¿Ver preview del archivo SQL generado?", default=True):
            self._show_sql_preview(sql_file)

        return True

    def _show_sql_preview(self, sql_file: str):
        """Muestra preview del archivo SQL generado"""
        console.print("\n📋 [bold]PREVIEW DEL ARCHIVO SQL[/bold]", style="blue")
        console.print("─" * 50)

        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Mostrar CREATE TABLE
            create_start = next(
                i for i, line in enumerate(lines) if "CREATE TABLE" in line
            )
            create_end = (
                next(i for i, line in enumerate(lines[create_start:]) if ");" in line)
                + create_start
                + 1
            )

            console.print("🏗️  [bold]CREATE TABLE:[/bold]")
            create_sql = "".join(lines[create_start:create_end])
            console.print(Panel(create_sql, border_style="cyan"))

            # Mostrar algunos INSERT
            insert_lines = [line for line in lines if line.startswith("INSERT")]
            console.print(
                f"\n📝 [bold]PRIMEROS INSERT STATEMENTS:[/bold] (mostrando 2 de {len(insert_lines)} total)"
            )

            for i, line in enumerate(insert_lines[:2]):
                console.print(f"[dim]{i + 1}.[/dim] {line.strip()}")

            if len(insert_lines) > 2:
                console.print("[dim]...[/dim]")

        except Exception as e:
            console.print(f"❌ [red]Error mostrando preview: {e}[/red]")


class CustomCSVToSQLConverter(CSVToSQLConverter):
    """Versión personalizada del convertidor con mapeo de columnas y manejo robusto de errores"""

    def __init__(
        self,
        csv_file_path: str,
        table_name: str,
        column_mapping: Dict[str, str],
        type_mapping: Dict[str, str],
        excluded_columns: List[str] = None,
        linkedin_columns_map: Dict[str, str] = None,
    ):
        super().__init__(csv_file_path, table_name)
        self.column_mapping = column_mapping
        self.type_mapping = type_mapping
        self.excluded_columns = excluded_columns or []
        self.linkedin_columns_map = linkedin_columns_map or {}  # Mapeo: col_linkedin → col_nombre
        self.error_count = 0
        self.skipped_lines = []

    def _detect_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Usa los tipos personalizados en lugar de detección automática"""
        result = {}
        for original_col in df.columns:
            new_col_name = self.column_mapping.get(original_col, original_col)
            sql_type = self.type_mapping.get(original_col, "TEXT")
            result[new_col_name] = sql_type
        return result

    def _is_name_column(self, column_name: str) -> bool:
        """
        Detecta si una columna contiene nombres basándose en el nombre de la columna
        """
        name_indicators = [
            "name",
            "nombre",
            "nom",
            "nome",  # Inglés, Español, Francés, Portugués
            "full_name",
            "fullname",
            "complete_name",
            "first_name",
            "firstname",
            "fname",
            "given_name",
            "last_name",
            "lastname",
            "lname",
            "surname",
            "family_name",
            "middle_name",
            "middlename",
            "mname",
            "nick_name",
            "nickname",
            "nick",
            "alias",
            "display_name",
            "screen_name",
            "user_name",
            "username",
            "contact_name",
            "person_name",
            "client_name",
            "customer_name",
            "employee_name",
            "staff_name",
            "member_name",
        ]

        column_lower = column_name.lower().strip()
        return any(indicator in column_lower for indicator in name_indicators)

    def _escape_sql_value(self, value, column_name: str = "") -> str:
        """
        Escapa valores para SQL con sanitización especial para nombres

        Args:
            value: Valor a escapar
            column_name: Nombre de la columna (para detectar si es un nombre)

        Returns:
            str: Valor escapado para SQL
        """
        if pd.isna(value) or value is None:
            return "NULL"

        # Convertir a string
        str_value = str(value).strip()
        if not str_value:
            return "NULL"

        # Si es una columna de nombres, aplicar sanitización
        if self._is_name_column(column_name):
            sanitized_name = sanitize_name(str_value)
            if sanitized_name is None:
                return "NULL"
            # Escapar comillas simples después de sanitizar
            escaped = sanitized_name.replace("'", "''")
            return f"'{escaped}'"

        # Para otros tipos de datos, usar escape normal
        if isinstance(value, str):
            # Escapar comillas simples
            escaped = str_value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            # Para otros tipos, escapar como string
            escaped = str_value.replace("'", "''")
            return f"'{escaped}'"

    def convert_to_sql(self, chunk_size: int = 1000, max_rows: int = None) -> str:
        """Conversión personalizada con mapeo de columnas y manejo robusto de errores"""
        logging.info(f"Iniciando conversión personalizada de {self.csv_file_path}")

        # Configurar archivo de salida
        base_name = os.path.splitext(os.path.basename(self.csv_file_path))[0]
        self.sql_file_path = f"{base_name}_custom_insert_statements.sql"

        # Reiniciar contadores
        self.error_count = 0
        self.skipped_lines = []

        try:
            # Detectar si el CSV tiene header
            header_option = detect_header(self.csv_file_path)

            # Leer muestra para crear estructura (con manejo de errores)
            sample_df = pd.read_csv(
                self.csv_file_path,
                nrows=1000,
                header=header_option,
                on_bad_lines="skip",
                dtype=str
            )

            # Si no hay header, renombrar columnas numéricas a nombres descriptivos
            if header_option is None:
                sample_df.columns = [f"col_{i}" for i in range(len(sample_df.columns))]
                logging.info("CSV sin header detectado. Nombres de columnas generados automáticamente.")

            # Aplicar exclusión de columnas primero
            if self.excluded_columns:
                columns_to_keep = [
                    col for col in sample_df.columns if col not in self.excluded_columns
                ]
                sample_df = sample_df[columns_to_keep]

            # Aplicar mapeo de columnas solo a las columnas restantes
            remaining_columns = list(sample_df.columns)
            sample_df.columns = [
                self.column_mapping.get(col, col) for col in remaining_columns
            ]

            # Extraer nombres de LinkedIn en la muestra si están configurados
            if self.linkedin_columns_map:
                for linkedin_col, name_col in self.linkedin_columns_map.items():
                    mapped_linkedin_col = self.column_mapping.get(linkedin_col, linkedin_col)
                    if mapped_linkedin_col in sample_df.columns:
                        sample_df[name_col] = extract_names_from_linkedin_batch(
                            sample_df[mapped_linkedin_col]
                        )
                        logging.info(f"Columna '{name_col}' agregada desde '{mapped_linkedin_col}'")

            # Obtener tipos personalizados solo para las columnas que no fueron excluidas
            column_types = {}
            for original_col, new_col in self.column_mapping.items():
                if original_col not in self.excluded_columns:
                    column_types[new_col] = self.type_mapping[original_col]

            # Agregar columnas de nombres extraídos de LinkedIn
            if self.linkedin_columns_map:
                for linkedin_col, name_col in self.linkedin_columns_map.items():
                    # Agregar la columna de nombre con tipo VARCHAR(255)
                    column_types[name_col] = "VARCHAR(255)"
                logging.info(f"Columnas de nombres desde LinkedIn agregadas: {list(self.linkedin_columns_map.values())}")

            # Crear archivo SQL
            with open(self.sql_file_path, "w", encoding="utf-8") as sql_file:
                # Header mejorado
                sql_file.write(f"-- Archivo SQL generado desde: {self.csv_file_path}\n")
                sql_file.write(
                    f"-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                sql_file.write("-- Conversión personalizada con mapeo de columnas\n")
                sql_file.write("-- Modo robusto: Ignora líneas malformadas\n\n")

                # CREATE TABLE personalizado
                create_table_sql = self.create_table_sql(column_types)
                sql_file.write(create_table_sql)

                # Procesar datos con manejo robusto de errores
                processed_rows = 0
                total_chunks = 0

                # Usar iterador robusto que maneja errores
                try:
                    # Determinar qué columnas leer (excluir las columnas seleccionadas por el usuario)
                    if self.excluded_columns:
                        # Leer todas las columnas primero para saber cuáles excluir
                        temp_df = pd.read_csv(
                            self.csv_file_path,
                            nrows=0,
                            header=header_option,
                            on_bad_lines="skip",
                            dtype=str
                        )
                        # Si no hay header, renombrar columnas
                        if header_option is None:
                            temp_df.columns = [f"col_{i}" for i in range(len(temp_df.columns))]

                        all_columns = temp_df.columns.tolist()
                        columns_to_read = [
                            col
                            for col in all_columns
                            if col not in self.excluded_columns
                        ]
                    else:
                        columns_to_read = None  # Leer todas las columnas

                    chunk_iterator = pd.read_csv(
                        self.csv_file_path,
                        chunksize=chunk_size,
                        header=header_option,
                        on_bad_lines="skip",  # Saltar líneas malformadas
                        dtype=str,  # Leer todo como string para evitar errores de tipo
                        usecols=columns_to_read,  # Solo leer las columnas que no fueron excluidas
                    )

                    for chunk_df in chunk_iterator:
                        total_chunks += 1

                        if max_rows and processed_rows >= max_rows:
                            break

                        # Si no hay header, renombrar columnas numéricas a nombres descriptivos
                        if header_option is None:
                            chunk_df.columns = [f"col_{i}" for i in range(len(chunk_df.columns))]

                        # Validar que el chunk tenga el número correcto de columnas
                        expected_cols = len(
                            [
                                col
                                for col in self.column_mapping.keys()
                                if col not in self.excluded_columns
                            ]
                        )
                        if len(chunk_df.columns) != expected_cols:
                            logging.warning(
                                f"Chunk {total_chunks}: Esperado {expected_cols} columnas, encontrado {len(chunk_df.columns)}"
                            )
                            # Ajustar columnas si es necesario
                            if len(chunk_df.columns) < expected_cols:
                                # Añadir columnas faltantes con None
                                for i in range(len(chunk_df.columns), expected_cols):
                                    chunk_df[f"missing_col_{i}"] = None
                            else:
                                # Truncar columnas extra
                                chunk_df = chunk_df.iloc[:, :expected_cols]

                        # Aplicar mapeo de columnas de forma segura
                        try:
                            # Obtener solo las columnas originales que no fueron excluidas
                            original_cols_remaining = [
                                col
                                for col in self.column_mapping.keys()
                                if col not in self.excluded_columns
                            ]
                            # Aplicar el mapeo usando las columnas reales del chunk
                            new_column_names = []
                            for i, actual_col in enumerate(chunk_df.columns):
                                if i < len(original_cols_remaining):
                                    original_col = original_cols_remaining[i]
                                    new_name = self.column_mapping.get(
                                        original_col, f"col_{i}"
                                    )
                                    new_column_names.append(new_name)
                                else:
                                    new_column_names.append(f"col_{i}")

                            chunk_df.columns = new_column_names
                        except Exception as e:
                            logging.warning(
                                f"Error en mapeo de columnas en chunk {total_chunks}: {e}"
                            )
                            # Usar mapeo básico como fallback
                            chunk_df.columns = [
                                f"col_{i}" for i in range(len(chunk_df.columns))
                            ]

                        # Extraer nombres desde URLs de LinkedIn si están configuradas
                        if self.linkedin_columns_map:
                            for linkedin_col, name_col in self.linkedin_columns_map.items():
                                # Verificar que la columna de LinkedIn esté en el chunk
                                mapped_linkedin_col = self.column_mapping.get(linkedin_col, linkedin_col)
                                if mapped_linkedin_col in chunk_df.columns:
                                    # Extraer nombres
                                    chunk_df[name_col] = extract_names_from_linkedin_batch(
                                        chunk_df[mapped_linkedin_col]
                                    )

                        # Procesar filas con manejo individual de errores
                        for idx, row in chunk_df.iterrows():
                            if max_rows and processed_rows >= max_rows:
                                break

                            try:
                                values = []
                                for col in chunk_df.columns:
                                    values.append(self._escape_sql_value(row[col], col))

                                values_str = ", ".join(values)
                                columns_str = ", ".join(chunk_df.columns)

                                insert_sql = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({values_str});\n"
                                sql_file.write(insert_sql)
                                processed_rows += 1

                            except Exception as e:
                                self.error_count += 1
                                error_info = (
                                    f"Chunk {total_chunks}, Fila {idx}: {str(e)[:100]}"
                                )
                                self.skipped_lines.append(error_info)
                                logging.warning(
                                    f"Error procesando fila {processed_rows + self.error_count}: {e}"
                                )
                                continue

                        # Log progreso cada 10 chunks
                        if total_chunks % 10 == 0:
                            logging.info(
                                f"Procesados {total_chunks} chunks, {processed_rows} filas válidas, {self.error_count} errores"
                            )

                except Exception as e:
                    logging.error(f"Error crítico en el procesamiento: {e}")
                    # Si hay un error crítico, al menos procesamos lo que tenemos

                # Footer con estadísticas
                success_rate = (
                    (processed_rows / (processed_rows + self.error_count)) * 100
                    if (processed_rows + self.error_count) > 0
                    else 100
                )

                sql_file.write("\n-- ESTADÍSTICAS DE CONVERSIÓN\n")
                sql_file.write(
                    f"-- Total de registros procesados exitosamente: {processed_rows}\n"
                )
                sql_file.write(
                    f"-- Total de errores/líneas omitidas: {self.error_count}\n"
                )
                sql_file.write(f"-- Tasa de éxito: {success_rate:.2f}%\n")
                sql_file.write(f"-- Chunks procesados: {total_chunks}\n")

                if self.error_count > 0 and len(self.skipped_lines) > 0:
                    sql_file.write("\n-- PRIMEROS 5 ERRORES ENCONTRADOS:\n")
                    for i, error in enumerate(self.skipped_lines[:5]):
                        sql_file.write(f"-- Error {i + 1}: {error}\n")

                sql_file.write("\nCOMMIT;\n")

            # Log final con estadísticas
            logging.info(
                f"Conversión completada. Archivo SQL creado: {self.sql_file_path}"
            )
            logging.info(f"Filas procesadas exitosamente: {processed_rows}")
            logging.info(f"Errores encontrados: {self.error_count}")
            logging.info(f"Tasa de éxito: {success_rate:.2f}%")

            # Mostrar estadísticas en consola si hay errores
            if self.error_count > 0:
                console.print(
                    f"\n⚠️ [yellow]Se encontraron {self.error_count} líneas con errores (omitidas)[/yellow]"
                )
                console.print(f"✅ [green]Tasa de éxito: {success_rate:.2f}%[/green]")
                console.print(
                    f"📊 [cyan]Filas válidas procesadas: {processed_rows:,}[/cyan]"
                )

            return self.sql_file_path

        except Exception as e:
            logging.error(f"Error durante la conversión personalizada: {str(e)}")
            raise


def show_main_menu():
    """Muestra el menú principal y devuelve la opción seleccionada"""
    console.clear()

    # Título principal
    title = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    🚀 CSV TO SQL CONVERTER - INTERACTIVE CLI 🚀               ║
║                                                               ║
║    ✨ Suite completa de herramientas SQL                      ║
║    🎨 Interfaz interactiva con animaciones                    ║
║    ⚙️ Control total sobre conversión y reparación             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """

    console.print(title, style="bold cyan")

    # Información del sistema
    info_table = Table(show_header=False, box=None)
    info_table.add_column("", style="dim")
    info_table.add_column("", style="bold")

    info_table.add_row("📅 Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    info_table.add_row("💻 Sistema:", "CSV to SQL Interactive Converter v2.1")
    info_table.add_row("🎯 Funciones:", "Conversión CSV → SQL + Reparación SQL")

    console.print(info_table)
    console.print()

    # Menú de opciones
    console.print("🎯 [bold]SELECCIONA UNA OPCIÓN:[/bold]\n")

    console.print("1️⃣  [cyan]Convertir CSV a SQL[/cyan] - Flujo principal de conversión")
    console.print(
        "2️⃣  [magenta]Reparar archivo SQL existente[/magenta] - Editar esquemas SQL"
    )
    if not SQL_REPAIR_AVAILABLE:
        console.print(
            "    [dim](Reparación SQL no disponible - falta sql_repair.py)[/dim]"
        )
    console.print("3️⃣  [yellow]Salir[/yellow]")
    console.print()

    while True:
        choice = Prompt.ask("Elige una opción", choices=["1", "2", "3"], default="1")

        if choice == "1":
            return "csv_conversion"
        elif choice == "2":
            if SQL_REPAIR_AVAILABLE:
                return "sql_repair"
            else:
                console.print(
                    "[red]❌ La funcionalidad de reparación SQL no está disponible[/red]"
                )
                continue
        elif choice == "3":
            return None
        else:
            console.print("[red]❌ Opción no válida[/red]")
            continue


@click.command()
@click.option(
    "--auto", is_flag=True, help="Ejecutar en modo automático sin interacciones"
)
def main(auto):
    """🚀 CSV to SQL Converter - CLI Interactivo"""

    if auto:
        console.print(
            "🤖 [yellow]Modo automático no implementado aún. Usando modo interactivo.[/yellow]"
        )

    try:
        # Mostrar menú principal
        mode = show_main_menu()

        if mode is None:
            console.print("👋 ¡Hasta luego!", style="yellow")
            return
        elif mode == "csv_conversion":
            # Flujo de conversión CSV
            converter = InteractiveCSVConverter()

            if not converter.show_welcome():
                return

            if not converter.select_csv_file():
                return

            if not converter.analyze_csv_structure():
                return

            if not converter.configure_table_name():
                return

            if not converter.configure_columns():
                return

            if not converter.show_configuration_summary():
                return

            if not converter.perform_conversion():
                return

            console.print(
                "\n🎉 [bold green]¡Conversión completada exitosamente![/bold green]"
            )
            console.print(
                "📚 [cyan]Consulta DATABASE_IMPORT_GUIDE.md para instrucciones de importación[/cyan]"
            )

        elif mode == "sql_repair":
            # Flujo de reparación SQL
            if not sql_repair_mode():
                console.print(
                    "[yellow]⚠️ No se pudo completar la reparación SQL[/yellow]"
                )
                return

            console.print(
                "\n🎉 [bold green]¡Reparación completada exitosamente![/bold green]"
            )

    except KeyboardInterrupt:
        console.print("\n\n👋 [yellow]Proceso interrumpido por el usuario[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]Error inesperado: {e}[/red]")


if __name__ == "__main__":
    main()
