#!/usr/bin/env python3
"""
Script para reparar archivos SQL con CREATE TABLE mal formados y/o generar INSERT statements desde VALUES.
"""

import argparse
import os
import re
import sys
import sqlite3
from typing import List, Tuple, Dict, Optional
from datetime import datetime

import pandas as pd
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.table import Table

# Importación opcional de PostgreSQL
try:
    import psycopg2
    import psycopg2.extras

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)

from csv_to_sql import CSVToSQLConverter

console = Console()


def parse_create_table(sql_text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Parsea un CREATE TABLE desde texto SQL y extrae nombre de tabla y columnas.
    Si no hay CREATE TABLE, intenta extraer desde VALUES.
    """
    # Buscar CREATE TABLE
    create_match = re.search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\);?",
        sql_text,
        re.IGNORECASE | re.DOTALL,
    )

    if create_match:
        table_name = create_match.group(1)
        columns_text = create_match.group(2)

        console.print(f"[green]✓ Detectado CREATE TABLE: {table_name}[/green]")

        # Parsear columnas
        columns = []
        for line in columns_text.strip().split("\n"):
            line = line.strip().rstrip(",")
            if line and not line.startswith("--"):
                parts = line.split()
                if len(parts) >= 2:
                    col_name = parts[0]
                    col_type = " ".join(parts[1:])
                    columns.append((col_name, col_type))
                else:
                    columns.append((line, "TEXT"))

        return table_name, columns

    # Si no hay CREATE TABLE, intentar parsear desde VALUES
    return parse_from_values(sql_text)


def parse_from_values(sql_text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Parsea un archivo SQL que solo contiene VALUES sin CREATE TABLE.
    Extrae los nombres de columnas de la primera línea.
    """
    lines = [line.strip() for line in sql_text.splitlines() if line.strip()]

    if not lines:
        raise ValueError("El archivo SQL está vacío")

    # Buscar la primera línea que contenga nombres de columnas entre paréntesis
    col_line = None
    for line in lines[:10]:  # Revisar las primeras 10 líneas
        if line.startswith("(") and "`" in line:
            col_line = line
            break

    if not col_line:
        raise ValueError(
            "No se pudieron detectar nombres de columnas. El archivo debe empezar con los nombres de columnas entre paréntesis como: (`col1`, `col2`, ...)"
        )

    # Extraer nombres de columnas
    # Remover paréntesis y dividir por comas
    col_content = col_line.strip("() ")
    col_names = []

    # Parsear nombres con backticks
    for part in col_content.split(","):
        part = part.strip()
        if part.startswith("`") and part.endswith("`"):
            col_name = part.strip("`")
        else:
            col_name = part.strip("'\"")
        col_names.append(col_name)

    console.print(f"[green]✓ Detectadas {len(col_names)} columnas desde VALUES[/green]")

    # Analizar algunos valores para inferir tipos
    columns = []
    for col_name in col_names:
        # Por defecto usar VARCHAR(255), luego el usuario puede cambiar
        inferred_type = "VARCHAR(255)"
        columns.append((col_name, inferred_type))

    # Sugerir nombre de tabla por defecto
    default_table_name = "imported_data"

    return default_table_name, columns


def render_columns_table(columns: List[Tuple[str, str]]):
    """Renderiza tabla de columnas detectadas"""
    table = Table(title="Columnas encontradas")
    table.add_column("#", style="dim")
    table.add_column("Nombre", style="cyan")
    table.add_column("Tipo", style="magenta")

    for i, (name, col_type) in enumerate(columns, 1):
        table.add_row(str(i), name, col_type)

    console.print(table)


def normalize_col_name(name: str) -> str:
    """Normaliza nombres de columnas para comparación"""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name.lower().strip())


def interactive_edit(
    table_name: str, columns: List[Tuple[str, str]]
) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Permite editar interactivamente el esquema de la tabla
    """
    console.print(
        Panel(
            f"Esquema detectado: [bold]{table_name}[/bold]",
            title="Paso 1: Esquema",
            border_style="green",
        )
    )

    render_columns_table(columns)

    # Paso 1: Seleccionar columnas a eliminar
    choices = [
        f"{i}. {name} ({col_type})" for i, (name, col_type) in enumerate(columns, 1)
    ]

    selected_to_remove = inquirer.checkbox(
        message="Selecciona columnas a eliminar (espacio para marcar, enter para confirmar):",
        choices=choices,
    )

    # Filtrar columnas no eliminadas
    indices_to_remove = set()
    for selected in selected_to_remove:
        index = int(selected.split(".")[0]) - 1
        indices_to_remove.add(index)

    filtered_columns = [
        col for i, col in enumerate(columns) if i not in indices_to_remove
    ]

    console.print(f"Columnas a mantener: {len(filtered_columns)}")

    # Paso 2: Renombrar y cambiar tipos
    console.print(
        Panel(
            "Ahora puedes renombrar cada columna o presionar enter para dejar igual.",
            title="Paso 2: Renombrar/Tipos",
            border_style="yellow",
        )
    )

    edited_columns = []
    for name, col_type in filtered_columns:
        new_name = Prompt.ask(f"Nombre para columna '{name}'", default=name)
        new_type = Prompt.ask(f"Tipo SQL para '{new_name}'", default=col_type)
        edited_columns.append((new_name, new_type))

    # Paso 3: Nombre de tabla
    new_table_name = Prompt.ask("Nombre de la tabla", default=table_name)

    return new_table_name, edited_columns, indices_to_remove


def build_create_table_sql(table_name: str, columns: List[Tuple[str, str]]) -> str:
    """Construye el SQL CREATE TABLE"""
    sql_lines = [
        f"DROP TABLE IF EXISTS {table_name};",
        "",
        f"CREATE TABLE {table_name} (",
        "",
    ]

    for name, col_type in columns:
        sql_lines.append(f"    {name} {col_type},")

    # Remover la última coma
    if sql_lines[-1].endswith(","):
        sql_lines[-1] = sql_lines[-1][:-1]

    sql_lines.extend(["", ");", ""])

    return "\n".join(sql_lines)


def ask_processing_option(total_values: int) -> int:
    """
    Pregunta al usuario cuántos VALUES quiere procesar usando las mismas opciones que CSV→SQL.
    Retorna el número de registros a procesar (0 = todos).
    """
    console.print(
        f"\n[cyan]📊 Se detectaron {total_values:,} VALUES en el archivo[/cyan]"
    )

    if total_values <= 100:
        console.print(
            "[green]El archivo es pequeño, procesando todos los registros.[/green]"
        )
        return 0

    choices = [
        "1. 🔍 Muestra rápida (100 registros)",
        "2. 📊 Mediano (10,000 registros)",
        "3. 📈 Todo el archivo completo",
        "4. 🎯 Personalizado (tú especificas cuántos)",
    ]

    console.print("\n[bold cyan]Opciones de procesamiento:[/bold cyan]")
    for choice in choices:
        console.print(f"  {choice}")

    while True:
        selection = Prompt.ask(
            "\n¿Qué opción eliges?", choices=["1", "2", "3", "4"], default="3"
        )

        if selection == "1":
            return 100
        elif selection == "2":
            return 10000
        elif selection == "3":
            return 0  # 0 significa todos
        elif selection == "4":
            break
        else:
            console.print("[red]⚠️ Por favor selecciona 1, 2, 3 o 4[/red]")

        # Personalizado
        while True:
            try:
                custom = Prompt.ask(
                    f"¿Cuántos registros procesar? (1 a {total_values:,})",
                    default="1000",
                )
                num = int(custom)
                if 1 <= num <= total_values:
                    return num
                else:
                    console.print(f"[red]⚠️ Debe estar entre 1 y {total_values:,}[/red]")
            except ValueError:
                console.print("[red]⚠️ Debe ser un número válido[/red]")


def sanitize_sql_value(value: str) -> str:
    """
    Sanitiza un valor individual para uso seguro en SQL (versión genérica).
    """
    return sanitize_sql_value_with_type(value, None)


def sanitize_sql_value_with_type(value: str, column_type: str = None) -> str:
    """
    Sanitiza un valor individual para uso seguro en SQL respetando el tipo de columna.
    """
    if not value or value.strip() == "":
        return "NULL"

    value = value.strip()

    # Si es NULL literal, devolverlo tal como está
    if value.upper() == "NULL":
        return "NULL"

    # Si ya tiene comillas, removerlas para limpiar
    if (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    ):
        value = value[1:-1]

    # Si el tipo de columna es numérico (INT, INTEGER, DECIMAL, FLOAT, REAL, NUMERIC)
    # y el valor es un número, devolverlo sin comillas
    if column_type and any(
        num_type in column_type.upper()
        for num_type in ["INT", "DECIMAL", "FLOAT", "REAL", "NUMERIC"]
    ):
        import re

        # Patrón para números: enteros, decimales (con o sin signo)
        number_pattern = r"^[-+]?(?:\d+\.?\d*|\.\d+)$"
        if re.match(number_pattern, value):
            return value

    # Para VARCHAR, CHAR, TEXT o cualquier otro tipo, siempre usar comillas
    # Solo para números sin tipo especificado, verificar si es número
    if column_type is None:
        import re

        # Patrón para números: enteros, decimales (con o sin signo)
        number_pattern = r"^[-+]?(?:\d+\.?\d*|\.\d+)$"
        if re.match(number_pattern, value):
            return value

    # ENFOQUE ROBUSTO: Decidir entre comillas simples o dobles según el contenido
    import re

    # 1. Limpiar caracteres de control peligrosos primero
    # Remover caracteres de control ASCII (0x00-0x1f) y DEL (0x7f)
    value = re.sub(r"[\x00-\x08\x0e-\x1f\x7f]", "", value)

    # 2. Remover caracteres Unicode de control extendidos
    value = re.sub(r"[\x80-\x9f]", "", value)

    # 3. Normalizar espacios en blanco
    value = value.replace("\n", " ")  # Saltos de línea a espacios
    value = value.replace("\r", " ")  # Retornos de carro a espacios
    value = value.replace("\t", " ")  # Tabs a espacios
    value = re.sub(r"\s+", " ", value)  # Múltiples espacios a uno solo
    value = value.strip()  # Limpiar espacios al inicio y final

    # 4. Truncar si es demasiado largo
    if len(value) > 65535:  # 64KB limit
        value = value[:65535]

    # 5. SANITIZAR APOSTROFES Y COMILLAS - SIEMPRE USAR COMILLAS SIMPLES
    # Enfoque: remover apostrofes problemáticos en lugar de usar comillas dobles

    # Opción 1: Escapar apostrofes duplicándolos (SQL estándar)
    # value = value.replace("'", "''")

    # Opción 2: Remover apostrofes completamente (más seguro y limpio)
    value = value.replace("'", "")  # Remover apostrofes: "UK's" -> "UKs"

    # También remover comillas dobles para evitar problemas
    value = value.replace('"', "")  # Remover comillas dobles

    # SIEMPRE usar comillas simples para strings en SQL
    return f"'{value}'"


def extract_filtered_values(
    value_block: str, kept_indices: List[int], column_types: List[str] = None
) -> str:
    """
    Extrae solo los valores de las columnas especificadas de un bloque VALUES.
    value_block: string como "(1001, 'teledyne.com', 'teledyne-technologies-incorporated', ...)"
    kept_indices: lista de índices de las columnas a mantener (0-based)
    """
    # Remover paréntesis y dividir por comas, respetando comillas
    value_block = value_block.strip()
    if value_block.startswith("(") and value_block.endswith(")"):
        value_block = value_block[1:-1]

    # Parsear valores respetando comillas y comas dentro de strings
    values = []
    current_value = ""
    in_quotes = False
    quote_char = None
    brace_depth = 0
    paren_depth = 0

    i = 0
    while i < len(value_block):
        char = value_block[i]

        if char in ["'", '"'] and (i == 0 or value_block[i - 1] != "\\"):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "," and not in_quotes and brace_depth == 0 and paren_depth == 0:
            values.append(current_value.strip())
            current_value = ""
            i += 1
            continue

        current_value += char
        i += 1

    # Añadir el último valor
    if current_value.strip():
        values.append(current_value.strip())

    # Extraer solo los valores de los índices especificados y sanitizarlos
    filtered_values = []
    for i, idx in enumerate(kept_indices):
        if idx < len(values):
            # Usar el tipo de columna si está disponible
            col_type = (
                column_types[i] if column_types and i < len(column_types) else None
            )
            sanitized_value = sanitize_sql_value_with_type(values[idx], col_type)
            filtered_values.append(sanitized_value)
        else:
            filtered_values.append("NULL")  # Valor por defecto si no existe

    return f"({', '.join(filtered_values)})"


def extract_insert_statements(
    sql_text: str,
    table_name: str,
    column_names: List[str],
    max_values: int = 0,
    kept_indices: List[int] = None,
    column_types: List[str] = None,
) -> str:
    """
    Extrae tanto INSERT statements existentes como VALUES sueltos del archivo SQL.
    max_values: número máximo de VALUES a procesar (0 = sin límite).
    kept_indices: lista de índices (0-based) de las columnas que se mantuvieron del archivo original.
    """
    insert_statements = []
    columns_str = ", ".join(column_names)

    # Dividir el texto en líneas para procesamiento
    lines = sql_text.splitlines()

    # Primero buscar INSERT statements existentes
    existing_inserts = []
    values_only = []

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detectar INSERT statements completos
        if stripped.upper().startswith("INSERT INTO"):
            # Intentar capturar el bloque VALUES
            insert_match = re.search(
                r"VALUES\s*(\(.*\))", stripped, re.IGNORECASE | re.DOTALL
            )
            if insert_match:
                values_part = insert_match.group(1)
                new_insert = (
                    f"INSERT INTO {table_name} ({columns_str}) VALUES {values_part};"
                )
                existing_inserts.append(new_insert)
            continue

        # Detectar VALUES sueltos (líneas que empiezan con paréntesis y número)
        if stripped.startswith("(") and len(stripped) > 10:
            match = re.match(r"^\(\s*(\d+)\s*,", stripped)
            if match:
                clean_line = stripped
                if clean_line.endswith(","):
                    clean_line = clean_line[:-1]
                values_only.append(clean_line)

    console.print(
        f"[cyan]Detectados {len(existing_inserts)} INSERT statements existentes[/cyan]"
    )
    console.print(
        f"[cyan]Detectados {len(values_only)} registros VALUES sueltos[/cyan]"
    )

    # Combinar INSERT statements existentes
    insert_statements.extend(existing_inserts)

    # Preguntar cuántos VALUES procesar si no se especificó max_values
    if max_values == 0 and len(values_only) > 0:
        max_values = ask_processing_option(len(values_only))

    # Aplicar límite si procede
    if max_values > 0 and len(values_only) > max_values:
        console.print(
            f"[yellow]⚠️ Procesando {max_values:,} de {len(values_only):,} VALUES[/yellow]"
        )
        values_only = values_only[:max_values]

    # Convertir VALUES sueltos a INSERT statements
    for i, value_block in enumerate(values_only):
        # Si tenemos información sobre los índices de las columnas que se mantuvieron,
        # extraer solo los valores de esas columnas
        if kept_indices:
            # Extraer valores del VALUES block usando los índices
            filtered_values = extract_filtered_values(
                value_block, kept_indices, column_types
            )
            insert_sql = (
                f"INSERT INTO {table_name} ({columns_str}) VALUES {filtered_values};"
            )
        else:
            # Usar el bloque original si no hay información de filtrado
            insert_sql = (
                f"INSERT INTO {table_name} ({columns_str}) VALUES {value_block};"
            )

        insert_statements.append(insert_sql)

        # Progress cada 100 líneas
        if (i + 1) % 100 == 0:
            console.print(f"[dim]Procesados {i + 1:,} VALUES...[/dim]")

    total_statements = len(existing_inserts) + len(values_only)
    console.print(
        f"[green]✓ Total: {total_statements:,} INSERT statements ({len(existing_inserts)} existentes + {len(values_only):,} desde VALUES)[/green]"
    )

    return "\n".join(insert_statements)


def try_generate_inserts_from_csv(
    csv_path: str, table_columns: List[str], output_file: str, table_name: str
):
    """
    Intenta generar INSERT statements leyendo CSV y mapeando columnas por nombre normalizado.
    """
    console.print(f"Intentando generar INSERTs desde CSV: {csv_path}")
    try:
        # Leer header
        df_hdr = pd.read_csv(csv_path, nrows=0)
        csv_cols = list(df_hdr.columns)
    except Exception as e:
        console.print(f"[red]Error leyendo header del CSV: {e}[/red]")
        return False

    # Normalizar nombres
    csv_norm = {normalize_col_name(c): c for c in csv_cols}
    mapping = {}
    for tcol in table_columns:
        key = normalize_col_name(tcol)
        if key in csv_norm:
            mapping[tcol] = csv_norm[key]
        else:
            mapping[tcol] = None

    console.print("Mapeo columnas tabla -> csv:")
    map_table = Table()
    map_table.add_column("Tabla")
    map_table.add_column("CSV")
    for tcol, ccol in mapping.items():
        map_table.add_row(tcol, ccol or "(ninguna)")
    console.print(map_table)

    # Preparar escape usando CSVToSQLConverter
    esc = CSVToSQLConverter(csv_path, table_name)

    # Leer por chunks y escribir INSERTs
    chunk_size = 1000
    total_written = 0
    try:
        with open(output_file, "a", encoding="utf-8") as out_f:
            for chunk in pd.read_csv(
                csv_path, chunksize=chunk_size, dtype=str, keep_default_na=False
            ):
                for _, row in chunk.iterrows():
                    values = []
                    for tcol in table_columns:
                        csvcol = mapping.get(tcol)
                        if csvcol and csvcol in row:
                            values.append(esc._escape_sql_value(row[csvcol]))
                        else:
                            values.append("NULL")
                    vals = ", ".join(values)
                    cols = ", ".join(table_columns)
                    out_f.write(f"INSERT INTO {table_name} ({cols}) VALUES ({vals});\n")
                    total_written += 1
    except Exception as e:
        console.print(f"[red]Error generando INSERTs: {e}[/red]")
        return False

    console.print(f"✅ Insert statements generados: {total_written}")
    return True


def ask_sqlite_processing_option() -> int:
    """
    Pregunta al usuario cuántos registros quiere procesar en SQLite.
    Retorna el número de registros a procesar (0 = todos).
    """
    choices = [
        "1. 🔍 Muestra rápida (100 registros)",
        "2. 📊 Mediano (500 registros)",
        "3. 📈 Grande (5,000 registros)",
        "4. 🗄️ Todo el archivo completo",
        "5. 🎯 Personalizado (tú especificas cuántos)",
    ]

    console.print("\n[bold cyan]Opciones de migración SQLite:[/bold cyan]")
    for choice in choices:
        console.print(f"  {choice}")

    while True:
        selection = Prompt.ask(
            "\n¿Qué opción eliges para SQLite?",
            choices=["1", "2", "3", "4", "5"],
            default="4",
        )

        if selection == "1":
            return 100
        elif selection == "2":
            return 500
        elif selection == "3":
            return 5000
        elif selection == "4":
            return 0  # 0 significa todos
        elif selection == "5":
            break
        else:
            console.print("[red]⚠️ Por favor selecciona 1, 2, 3, 4 o 5[/red]")

        # Personalizado
        while True:
            try:
                custom = Prompt.ask(
                    "¿Cuántos registros migrar a SQLite?", default="500"
                )
                num = int(custom)
                if num > 0:
                    return num
                else:
                    console.print("[red]⚠️ Debe ser un número mayor a 0[/red]")
            except ValueError:
                console.print("[red]⚠️ Debe ser un número válido[/red]")


def get_postgres_credentials() -> Dict[str, str]:
    """
    Recopila las credenciales de PostgreSQL del usuario.
    """
    console.print(
        Panel(
            "🐘 Configuración de PostgreSQL\n"
            "Proporciona los datos de conexión a tu base de datos PostgreSQL.",
            title="Credenciales de PostgreSQL",
            border_style="blue",
        )
    )

    credentials = {}

    # Host
    credentials["host"] = Prompt.ask("[cyan]Host/Servidor[/cyan]", default="localhost")

    # Puerto
    credentials["port"] = str(IntPrompt.ask("[cyan]Puerto[/cyan]", default=5432))

    # Base de datos
    credentials["database"] = Prompt.ask("[cyan]Nombre de la base de datos[/cyan]")

    # Usuario
    credentials["user"] = Prompt.ask("[cyan]Usuario[/cyan]")

    # Contraseña (sin mostrar)
    credentials["password"] = Prompt.ask("[cyan]Contraseña[/cyan]", password=True)

    return credentials


def test_postgres_connection(credentials: Dict[str, str]) -> bool:
    """
    Prueba la conexión a PostgreSQL con las credenciales proporcionadas.
    """
    try:
        conn = psycopg2.connect(**credentials)
        conn.close()
        console.print("[green]✓ Conexión exitosa a PostgreSQL[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Error de conexión: {e}[/red]")
        return False


def create_postgres_from_sql(
    sql_file: str, table_name: str, credentials: Dict[str, str], max_inserts: int = 0
) -> bool:
    """
    Crea tabla e inserta datos en PostgreSQL ejecutando el archivo SQL generado.
    max_inserts: número máximo de INSERT statements a procesar (0 = todos).
    Retorna True si fue exitoso.
    """
    console.print(
        f"[cyan]🐘 Creando tabla y datos en PostgreSQL: {credentials['database']}[/cyan]"
    )

    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(**credentials)
        conn.autocommit = False  # Usar transacciones manuales
        cursor = conn.cursor()

        # Leer el archivo SQL
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Dividir en CREATE TABLE e INSERTs
        create_match = re.search(
            r"(CREATE TABLE.*?;)", sql_content, re.IGNORECASE | re.DOTALL
        )

        if not create_match:
            console.print("[red]❌ No se encontró CREATE TABLE en el archivo[/red]")
            return False

        create_sql = create_match.group(1)

        # Ejecutar CREATE TABLE
        console.print("[cyan]📋 Creando tabla...[/cyan]")

        # Agregar DROP TABLE IF EXISTS para evitar conflictos
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_sql)
        cursor.execute(create_sql)

        # Procesar INSERTs
        insert_pattern = r"INSERT INTO \w+ VALUES \([^)]+\);"
        inserts = re.findall(insert_pattern, sql_content, re.IGNORECASE)

        total_inserts = len(inserts)
        if max_inserts > 0 and max_inserts < total_inserts:
            inserts = inserts[:max_inserts]
            console.print(
                f"[yellow]⚠️ Limitando a {max_inserts} de {total_inserts} registros[/yellow]"
            )

        console.print(f"[cyan]📊 Insertando {len(inserts)} registros...[/cyan]")

        # Progreso de inserción
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Insertando datos...", total=len(inserts))

            batch_size = 1000
            for i in range(0, len(inserts), batch_size):
                batch = inserts[i : i + batch_size]

                for insert_sql in batch:
                    cursor.execute(insert_sql)

                # Commit cada batch
                conn.commit()
                progress.update(task, advance=len(batch))

        # Verificar datos insertados
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        console.print(f"[green]✅ Base de datos PostgreSQL creada exitosamente[/green]")
        console.print(f"[cyan]📊 Registros insertados: {count:,}[/cyan]")
        console.print(f"[cyan]🗄️ Tabla: {table_name}[/cyan]")
        console.print(
            f"[cyan]🔗 Host: {credentials['host']}:{credentials['port']}/{credentials['database']}[/cyan]"
        )

        conn.close()
        return True

    except Exception as e:
        console.print(f"[red]❌ Error creando base de datos PostgreSQL: {e}[/red]")
        if "conn" in locals():
            conn.rollback()
            conn.close()
        return False


def create_sqlite_from_sql(
    sql_file: str, table_name: str, max_inserts: int = 0, original_sql_file: str = None
) -> str:
    """
    Crea una base de datos SQLite ejecutando el archivo SQL generado.
    max_inserts: número máximo de INSERT statements a procesar (0 = todos).
    original_sql_file: archivo SQL original para obtener más datos si es necesario.
    Retorna la ruta del archivo SQLite creado.
    """
    # Generar nombre del archivo SQLite
    base_name = os.path.splitext(os.path.basename(sql_file))[0]
    sqlite_file = os.path.join(os.path.dirname(sql_file), f"{base_name}.db")

    console.print(f"[cyan]🗄️ Creando base de datos SQLite: {sqlite_file}[/cyan]")

    try:
        # Conectar a SQLite (se crea automáticamente si no existe)
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        # Leer el archivo SQL
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Dividir en statements individuales
        statements = sql_content.split(";")
        all_statements = [s for s in statements if s.strip()]

        # Separar CREATE TABLE de INSERT statements
        create_statements = []
        insert_statements = []

        for stmt in all_statements:
            stmt_upper = stmt.strip().upper()
            if "CREATE TABLE" in stmt_upper or "DROP TABLE" in stmt_upper:
                create_statements.append(stmt)
            elif "INSERT INTO" in stmt_upper:
                insert_statements.append(stmt)

        # Aplicar límite a INSERT statements si se especificó
        if max_inserts > 0 and len(insert_statements) > max_inserts:
            console.print(
                f"[yellow]⚠️ Limitando a {max_inserts:,} INSERT statements de {len(insert_statements):,} totales[/yellow]"
            )
            insert_statements = insert_statements[:max_inserts]

        # Combinar statements para ejecutar
        final_statements = create_statements + insert_statements
        total_statements = len(final_statements)

        console.print(
            f"[cyan]📊 Ejecutando {len(create_statements)} CREATE statements + {len(insert_statements):,} INSERT statements...[/cyan]"
        )

        with Progress() as progress:
            task = progress.add_task(
                "[green]Ejecutando migraciones...", total=total_statements
            )

            executed = 0
            errors = 0
            for i, statement in enumerate(final_statements):
                statement = statement.strip()
                if statement:  # Solo ejecutar statements no vacíos
                    try:
                        cursor.execute(statement)
                        executed += 1

                        # Actualizar progreso cada 100 statements para archivos pequeños
                        if executed % max(100, total_statements // 10) == 0:
                            progress.update(
                                task, advance=max(100, total_statements // 10)
                            )

                    except sqlite3.Error as e:
                        errors += 1
                        # Solo mostrar los primeros 5 errores para evitar spam
                        if errors <= 5:
                            error_msg = str(e)[:80] + (
                                "..." if len(str(e)) > 80 else ""
                            )
                            console.print(
                                f"[dim yellow]⚠️ Error en statement {i + 1}: {error_msg}[/dim yellow]"
                            )
                        elif errors == 6:
                            console.print(
                                "[dim yellow]... (más errores suprimidos para mantener legibilidad)[/dim yellow]"
                            )

            # Completar el progreso
            progress.update(task, completed=total_statements)

            if errors > 0:
                console.print(
                    f"[yellow]⚠️ Se encontraron {errors} errores durante la ejecución (probablemente caracteres especiales)[/yellow]"
                )

        # Commit y obtener estadísticas
        conn.commit()

        # Contar registros insertados
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        record_count = cursor.fetchone()[0]

        # Obtener tamaño del archivo SQLite
        conn.close()
        sqlite_size = os.path.getsize(sqlite_file) / (1024 * 1024)  # MB

        console.print(f"[green]✅ Base de datos SQLite creada exitosamente[/green]")
        console.print(f"[green]📊 Registros insertados: {record_count:,}[/green]")
        console.print(
            f"[green]💾 Tamaño de la base de datos: {sqlite_size:.2f} MB[/green]"
        )

        return sqlite_file

    except Exception as e:
        console.print(f"[red]❌ Error creando SQLite: {e}[/red]")
        if os.path.exists(sqlite_file):
            os.remove(sqlite_file)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Reparar un CREATE TABLE mal armado y/o generar SQL completo desde VALUES"
    )
    parser.add_argument("sql_file", help="Ruta al archivo SQL a reparar")
    args = parser.parse_args()

    sql_path = args.sql_file
    if not os.path.exists(sql_path):
        console.print(f"[red]No existe el archivo: {sql_path}[/red]")
        sys.exit(1)

    sql_text = open(sql_path, "r", encoding="utf-8", errors="ignore").read()

    try:
        table_name, columns = parse_create_table(sql_text)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # Interacción para editar esquema
    new_table_name, edited_columns, indices_to_remove = interactive_edit(
        table_name, columns
    )

    # Generar SQL corregido
    base = os.path.splitext(os.path.basename(sql_path))[0]
    out_file = os.path.join(os.path.dirname(sql_path), f"{base}_corrected.sql")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("-- Archivo SQL corregido/generado por CSV to SQL Converter CLI\n")
        f.write(f"-- Fuente: {sql_path}\n")
        f.write(f"-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Escribir CREATE TABLE
        corrected_sql = build_create_table_sql(new_table_name, edited_columns)
        f.write(corrected_sql)

        # Siempre buscar y generar INSERTs desde VALUES existentes o INSERT statements
        console.print(
            "[cyan]Buscando INSERT statements y VALUES en el archivo original...[/cyan]"
        )
        column_names = [col[0] for col in edited_columns]
        column_types = [col[1] for col in edited_columns]

        # Crear lista de índices de columnas que se mantuvieron (0-based)
        kept_indices = [i for i in range(len(columns)) if i not in indices_to_remove]

        insert_sql = extract_insert_statements(
            sql_text, new_table_name, column_names, 0, kept_indices, column_types
        )

        if insert_sql.strip():  # Solo escribir si encontramos INSERT statements
            f.write("\n-- INSERT statements (existentes y extraídos desde VALUES)\n")
            f.write(insert_sql)
        else:
            console.print(
                "[yellow]⚠️ No se encontraron INSERT statements ni VALUES en el archivo[/yellow]"
            )

    console.print(
        Panel(
            f"SQL corregido escrito en: [bold]{out_file}[/bold]",
            title="✅ Completado",
            border_style="green",
        )
    )

    # Mostrar estadísticas del archivo generado
    file_size = os.path.getsize(out_file) / (1024 * 1024)  # MB
    console.print(f"📊 Tamaño del archivo generado: {file_size:.2f} MB")

    # Preguntar si quiere generar inserts adicionales desde CSV
    if not insert_sql.strip() and Confirm.ask(
        "¿No se encontraron VALUES. Deseas generar INSERTs desde un CSV?", default=False
    ):
        csv_path = Prompt.ask("Ruta al CSV (absoluta o relativa)")
        if not os.path.exists(csv_path):
            console.print(f"[red]CSV no encontrado: {csv_path}[/red]")
        else:
            # Anexar al mismo archivo
            ok = try_generate_inserts_from_csv(
                csv_path, [c[0] for c in edited_columns], out_file, new_table_name
            )
            if ok:
                console.print(
                    f"[green]Archivo final con CREATE + INSERTs: {out_file}[/green]"
                )

    # Menú de selección de base de datos
    console.print("\n" + "=" * 80)
    console.print(
        Panel(
            "¿Deseas crear una base de datos para importar los datos?\n"
            "Puedes elegir entre SQLite (archivo local) o PostgreSQL (servidor).",
            title="🗄️ Crear Base de Datos",
            border_style="cyan",
        )
    )

    # Preparar opciones del menú
    db_options = [
        ("📄 SQLite", "Local - Crear archivo .db (recomendado para pruebas)"),
        ("🐘 PostgreSQL", "Servidor - Conectar a PostgreSQL (producción)"),
        ("❌ Ninguna", "Solo generar archivo SQL"),
    ]

    # Si PostgreSQL no está disponible, agregar nota
    if not POSTGRES_AVAILABLE:
        db_options[1] = (
            "🐘 PostgreSQL [DESHABILITADO]",
            "Requiere: pip install psycopg2-binary",
        )

    # Mostrar menú
    choices = [f"{option[0]} - {option[1]}" for option in db_options]

    selected = inquirer.list_input(
        "Selecciona el tipo de base de datos:", choices=choices
    )

    # Procesar selección
    if "SQLite" in selected:
        # Opción SQLite
        sqlite_file = create_sqlite_from_sql(out_file, new_table_name)
        if sqlite_file:
            console.print(f"\n[green]🎉 ¡Base de datos SQLite lista![/green]")
            console.print(f"[cyan]📍 Ubicación: {sqlite_file}[/cyan]")
            console.print(f"[dim]Puedes usar: sqlite3 {sqlite_file}[/dim]")
        else:
            console.print("[red]❌ No se pudo crear la base de datos SQLite[/red]")

    elif "PostgreSQL" in selected and POSTGRES_AVAILABLE:
        # Opción PostgreSQL
        credentials = get_postgres_credentials()

        # Probar conexión
        if test_postgres_connection(credentials):
            # Preguntar por límite de registros para pruebas
            if Confirm.ask(
                "¿Deseas limitar el número de registros para pruebas?", default=False
            ):
                max_records = IntPrompt.ask("Número máximo de registros", default=1000)
            else:
                max_records = 0

            # Crear base de datos
            success = create_postgres_from_sql(
                out_file, new_table_name, credentials, max_records
            )
            if success:
                console.print(f"\n[green]🎉 ¡Base de datos PostgreSQL lista![/green]")
            else:
                console.print(
                    "[red]❌ No se pudo crear la base de datos PostgreSQL[/red]"
                )
        else:
            console.print(
                "[red]❌ No se pudo conectar a PostgreSQL. Verifica las credenciales.[/red]"
            )

    elif "PostgreSQL" in selected and not POSTGRES_AVAILABLE:
        # PostgreSQL no disponible
        console.print("[yellow]⚠️ PostgreSQL no está disponible.[/yellow]")
        console.print("[dim]Instala con: pip install psycopg2-binary[/dim]")

    else:
        # Solo archivo SQL
        console.print("[cyan]📄 Solo se generó el archivo SQL corregido.[/cyan]")

    console.print("\n🎉 Proceso finalizado.")


if __name__ == "__main__":
    main()
