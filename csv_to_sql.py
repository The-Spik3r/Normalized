#!/usr/bin/env python3
"""
CSV to SQL Converter
Convierte archivos CSV grandes a archivos SQL con INSERT statements
"""

import pandas as pd
import os
import re
from typing import Dict, Any
import logging
from datetime import datetime
import unicodedata

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("csv_to_sql.log"), logging.StreamHandler()],
)


class CSVToSQLConverter:
    def __init__(self, csv_file_path: str, table_name: str = None):
        """
        Inicializa el convertidor CSV a SQL

        Args:
            csv_file_path (str): Ruta al archivo CSV
            table_name (str): Nombre de la tabla SQL (opcional)
        """
        self.csv_file_path = csv_file_path
        self.table_name = table_name or self._generate_table_name()
        self.sql_file_path = None

    def _robust_sanitize_value(self, value: str) -> str:
        """
        Sanitización robusta para valores problemáticos

        Args:
            value (str): Valor a sanitizar

        Returns:
            str: Valor sanitizado
        """
        if not isinstance(value, str):
            return str(value)

        # Normalizar Unicode para detectar caracteres problemáticos
        normalized = unicodedata.normalize("NFKC", str(value))

        # Limpiar y escapar en orden específico
        sanitized = (
            normalized.strip()
            .replace("\\", "\\\\")  # Escapar backslashes PRIMERO
            .replace("'", "''")  # Escapar comillas simples
            .replace('"', '""')  # Escapar comillas dobles por si acaso
            .replace("\t", "\\t")  # Escapar tabs
            .replace("\n", "\\n")  # Escapar saltos de línea
            .replace("\r", "\\r")  # Escapar retornos de carro
            .replace("\x00", "")  # Eliminar NULL bytes
            .replace("\x1a", "")  # Eliminar SUB (Substitute) caracteres
            .replace("\x08", "")  # Eliminar backspace
            .replace("\x0b", "")  # Eliminar vertical tab
            .replace("\x0c", "")  # Eliminar form feed
        )

        # Eliminar otros caracteres de control problemáticos
        sanitized = "".join(
            char
            for char in sanitized
            if unicodedata.category(char) != "Cc" or char in "\t\n\r"
        )

        return sanitized

    def _generate_table_name(self) -> str:
        """Genera un nombre de tabla basado en el nombre del archivo"""
        filename = os.path.basename(self.csv_file_path)
        # Remover extensión y caracteres especiales
        table_name = re.sub(r"[^a-zA-Z0-9_]", "_", filename.split(".")[0])
        # Asegurar que comience con letra
        if table_name[0].isdigit():
            table_name = "table_" + table_name
        return table_name.lower()

    def _detect_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detecta los tipos de datos de las columnas del DataFrame

        Args:
            df (pd.DataFrame): DataFrame a analizar

        Returns:
            Dict[str, str]: Diccionario con nombres de columnas y tipos SQL
        """
        type_mapping = {}

        for column in df.columns:
            # Limpiar nombre de columna
            clean_column = re.sub(r"[^a-zA-Z0-9_]", "_", str(column))
            if clean_column[0].isdigit():
                clean_column = "col_" + clean_column

            # Detectar tipo de dato
            if df[column].dtype == "object":
                # Verificar si es fecha
                try:
                    pd.to_datetime(df[column].dropna().iloc[:100])
                    type_mapping[clean_column] = "DATETIME"
                except Exception:
                    # Determinar tamaño de VARCHAR
                    max_length = df[column].astype(str).str.len().max()
                    varchar_size = min(max(max_length, 50), 1000)
                    type_mapping[clean_column] = f"VARCHAR({varchar_size})"
            elif df[column].dtype in ["int64", "int32"]:
                type_mapping[clean_column] = "INT"
            elif df[column].dtype in ["float64", "float32"]:
                type_mapping[clean_column] = "DECIMAL(10,2)"
            elif df[column].dtype == "bool":
                type_mapping[clean_column] = "BOOLEAN"
            else:
                type_mapping[clean_column] = "TEXT"

        return type_mapping

    def _escape_sql_value(self, value: Any) -> str:
        """
        Escapa valores para SQL

        Args:
            value: Valor a escapar

        Returns:
            str: Valor escapado para SQL
        """
        if pd.isna(value) or value is None:
            return "NULL"
        elif isinstance(value, str):
            # Escapar comillas simples
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return f"'{str(value)}'"

    def create_table_sql(self, column_types: Dict[str, str]) -> str:
        """
        Crea el SQL para crear la tabla

        Args:
            column_types (Dict[str, str]): Tipos de datos de las columnas

        Returns:
            str: SQL CREATE TABLE statement
        """
        # No generar CREATE TABLE ni DROP TABLE, solo comentario
        return f"-- Tabla: {self.table_name}\n\n"

    def _generate_copy_statement(self, sql_file, max_rows: int = None) -> int:
        """
        Genera un COPY statement con datos incrustados usando STDIN

        Args:
            sql_file: Archivo SQL abierto para escritura
            max_rows (int): Máximo número de filas a procesar

        Returns:
            int: Número de filas procesadas
        """
        # Leer datos del CSV
        if max_rows:
            df = pd.read_csv(self.csv_file_path, nrows=max_rows)
        else:
            df = pd.read_csv(self.csv_file_path)

        # Limpiar nombres de columnas
        clean_columns = []
        for col in df.columns:
            clean_col = re.sub(r"[^a-zA-Z0-9_]", "_", str(col))
            if clean_col[0].isdigit():
                clean_col = "col_" + clean_col
            clean_columns.append(clean_col)

        df.columns = clean_columns

        # Generar header del COPY statement con formato multilinea
        columns_formatted = ",\n    ".join(clean_columns)
        copy_header = f"""-- COPY command with inline data
COPY {self.table_name} (
    {columns_formatted}
) FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t', NULL '\\\\N');
"""
        sql_file.write(copy_header)

        # Procesar datos fila por fila
        processed_rows = 0
        for _, row in df.iterrows():
            if max_rows and processed_rows >= max_rows:
                break

            # Convertir valores a formato COPY (usar \N para NULL, tab como separador)
            values = []
            for col in clean_columns:
                value = row[col]
                if pd.isna(value) or value is None or value == "":
                    values.append("\\N")  # Sin comillas para NULL
                elif isinstance(value, str):
                    # Usar sanitización robusta
                    sanitized = self._robust_sanitize_value(value)

                    # Envolver en comillas simples para proteger de operadores y caracteres especiales
                    values.append(f"'{sanitized}'")
                else:
                    # Para números y otros tipos, convertir a string y envolver en comillas simples
                    values.append(f"'{str(value)}'")

            # Escribir línea con tabs como separadores
            line = "\t".join(values) + "\n"
            sql_file.write(line)
            processed_rows += 1

        # Terminar COPY statement
        sql_file.write(".\n\n")

        return processed_rows

    def _generate_insert_statements(
        self, sql_file, chunk_size: int, max_rows: int = None
    ) -> int:
        """
        Genera INSERT statements individuales

        Args:
            sql_file: Archivo SQL abierto para escritura
            chunk_size (int): Tamaño del chunk para procesar en lotes
            max_rows (int): Máximo número de filas a procesar

        Returns:
            int: Número de filas procesadas
        """
        processed_rows = 0

        for chunk_df in pd.read_csv(self.csv_file_path, chunksize=chunk_size):
            if max_rows and processed_rows >= max_rows:
                break

            # Limpiar nombres de columnas
            chunk_df.columns = [
                re.sub(r"[^a-zA-Z0-9_]", "_", str(col)) for col in chunk_df.columns
            ]
            chunk_df.columns = [
                f"col_{col}" if col[0].isdigit() else col for col in chunk_df.columns
            ]

            # Generar INSERT statements
            for _, row in chunk_df.iterrows():
                if max_rows and processed_rows >= max_rows:
                    break

                values = []
                for col in chunk_df.columns:
                    values.append(self._escape_sql_value(row[col]))

                values_str = ", ".join(values)
                columns_str = ", ".join(chunk_df.columns)

                insert_sql = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({values_str});\n"
                sql_file.write(insert_sql)

                processed_rows += 1

                if processed_rows % 1000 == 0:
                    logging.info(f"Procesadas {processed_rows} filas...")

        return processed_rows

    def convert_to_sql(
        self, chunk_size: int = 1000, max_rows: int = None, use_copy: bool = False
    ) -> str:
        """
        Convierte el archivo CSV a SQL

        Args:
            chunk_size (int): Tamaño del chunk para procesar en lotes
            max_rows (int): Máximo número de filas a procesar (None para todas)
            use_copy (bool): Si True, genera COPY statement; si False, genera INSERT statements

        Returns:
            str: Ruta del archivo SQL generado
        """
        logging.info(f"Iniciando conversión de {self.csv_file_path}")

        # Configurar archivo de salida
        base_name = os.path.splitext(os.path.basename(self.csv_file_path))[0]
        method_suffix = "copy_statement" if use_copy else "insert_statements"
        self.sql_file_path = f"{base_name}_{method_suffix}.sql"

        try:
            # Leer muestra para detectar tipos de datos
            logging.info("Detectando estructura del archivo...")
            sample_df = pd.read_csv(self.csv_file_path, nrows=1000)
            column_types = self._detect_data_types(sample_df)

            # Crear archivo SQL
            with open(self.sql_file_path, "w", encoding="utf-8") as sql_file:
                # Escribir header
                sql_file.write(f"-- {os.path.basename(self.sql_file_path)}\n\n")
                sql_file.write(f"-- Archivo SQL generado desde: {self.csv_file_path}\n")
                sql_file.write(
                    f"-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )

                # Start transaction for safety
                sql_file.write("-- Start transaction for safety\n")
                sql_file.write("BEGIN;\n\n")

                # Escribir CREATE TABLE
                create_table_sql = self.create_table_sql(column_types)
                sql_file.write(create_table_sql)

                if use_copy:
                    # Método COPY - mucho más rápido
                    logging.info("Generando COPY statement...")
                    processed_rows = self._generate_copy_statement(sql_file, max_rows)
                else:
                    # Método INSERT tradicional
                    logging.info("Generando INSERT statements...")
                    processed_rows = self._generate_insert_statements(
                        sql_file, chunk_size, max_rows
                    )

                # Escribir footer
                sql_file.write(
                    f"\n-- Total de registros procesados: {processed_rows}\n"
                )
                sql_file.write("COMMIT;\n")

            logging.info(
                f"Conversión completada. Archivo SQL creado: {self.sql_file_path}"
            )
            logging.info(f"Total de filas procesadas: {processed_rows}")

            return self.sql_file_path

        except Exception as e:
            logging.error(f"Error durante la conversión: {str(e)}")
            raise


def main():
    """Función principal para usar desde línea de comandos"""
    import argparse

    parser = argparse.ArgumentParser(description="Convierte archivos CSV a SQL")
    parser.add_argument("csv_file", help="Ruta al archivo CSV")
    parser.add_argument("--table-name", help="Nombre de la tabla SQL")
    parser.add_argument(
        "--chunk-size", type=int, default=1000, help="Tamaño del chunk (default: 1000)"
    )
    parser.add_argument(
        "--max-rows", type=int, help="Máximo número de filas a procesar"
    )
    parser.add_argument(
        "--use-copy",
        action="store_true",
        help="Usar COPY statement en lugar de INSERT (mucho más rápido)",
    )

    args = parser.parse_args()

    # Crear convertidor
    converter = CSVToSQLConverter(args.csv_file, args.table_name)

    # Convertir a SQL
    sql_file = converter.convert_to_sql(
        chunk_size=args.chunk_size, max_rows=args.max_rows, use_copy=args.use_copy
    )

    method = "COPY statement" if args.use_copy else "INSERT statements"
    print(f"Archivo SQL creado: {sql_file}")
    print(f"Método utilizado: {method}")


if __name__ == "__main__":
    main()
