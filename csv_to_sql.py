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
        columns_sql = []
        for column, data_type in column_types.items():
            columns_sql.append(f"    {column} {data_type}")

        create_sql = f"""-- Crear tabla {self.table_name}
DROP TABLE IF EXISTS {self.table_name};

CREATE TABLE {self.table_name} (
{",{}".format(chr(10)).join(columns_sql)}
);

"""
        return create_sql

    def convert_to_sql(self, chunk_size: int = 1000, max_rows: int = None) -> str:
        """
        Convierte el archivo CSV a SQL

        Args:
            chunk_size (int): Tamaño del chunk para procesar en lotes
            max_rows (int): Máximo número de filas a procesar (None para todas)

        Returns:
            str: Ruta del archivo SQL generado
        """
        logging.info(f"Iniciando conversión de {self.csv_file_path}")

        # Configurar archivo de salida
        base_name = os.path.splitext(os.path.basename(self.csv_file_path))[0]
        self.sql_file_path = f"{base_name}_insert_statements.sql"

        try:
            # Leer muestra para detectar tipos de datos
            logging.info("Detectando estructura del archivo...")
            sample_df = pd.read_csv(self.csv_file_path, nrows=1000)
            column_types = self._detect_data_types(sample_df)

            # Crear archivo SQL
            with open(self.sql_file_path, "w", encoding="utf-8") as sql_file:
                # Escribir header
                sql_file.write(f"-- Archivo SQL generado desde: {self.csv_file_path}\n")
                sql_file.write(
                    f"-- Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )

                # Escribir CREATE TABLE
                create_table_sql = self.create_table_sql(column_types)
                sql_file.write(create_table_sql)

                # Procesar CSV en chunks
                logging.info("Procesando datos...")
                processed_rows = 0

                for chunk_df in pd.read_csv(self.csv_file_path, chunksize=chunk_size):
                    if max_rows and processed_rows >= max_rows:
                        break

                    # Limpiar nombres de columnas
                    chunk_df.columns = [
                        re.sub(r"[^a-zA-Z0-9_]", "_", str(col))
                        for col in chunk_df.columns
                    ]
                    chunk_df.columns = [
                        f"col_{col}" if col[0].isdigit() else col
                        for col in chunk_df.columns
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

                # Escribir footer
                sql_file.write(
                    f"\n-- Total de registros insertados: {processed_rows}\n"
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

    args = parser.parse_args()

    # Crear convertidor
    converter = CSVToSQLConverter(args.csv_file, args.table_name)

    # Convertir a SQL
    sql_file = converter.convert_to_sql(
        chunk_size=args.chunk_size, max_rows=args.max_rows
    )

    print(f"Archivo SQL creado: {sql_file}")


if __name__ == "__main__":
    main()
