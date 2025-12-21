from typing import Dict, List, Tuple

import pymysql, os, json
from pymysql.cursors import DictCursor

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=DictCursor,
    )


def get_mysql_database_schema() -> Dict[str, Dict]:
    """
    Introspect MySQL INFORMATION_SCHEMA and build a schema dict:
    {
        "TableName": {
            "columns": [
                {"name": ..., "type": ..., "nullable": ..., "default": ...},
            ],
            "primary_key": ["col1", ...],
            "foreign_keys": [
                {
                    "column": "...",
                    "references_table": "...",
                    "references_column": "...",
                    "constraint_name": "...",
                },
            ],
        },
        ...
    }
    """
    schema: Dict[str, Dict] = {}

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # All tables
            cur.execute(
                """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = %s
                """,
                (DB_NAME,),
            )
            tables = [row["TABLE_NAME"] for row in cur.fetchall()]

            # Columns
            cur.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE,
                       COLUMN_KEY, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                (DB_NAME,),
            )
            col_rows = cur.fetchall()

            # Foreign keys
            cur.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
                       REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                """,
                (DB_NAME,),
            )
            fk_rows = cur.fetchall()

        # Initialize tables
        for t in tables:
            schema[t] = {
                "columns": [],
                "primary_key": [],
                "foreign_keys": [],
            }

        # Fill columns and PK
        for row in col_rows:
            tname = row["TABLE_NAME"]
            if tname not in schema:
                continue
            schema[tname]["columns"].append(
                {
                    "name": row["COLUMN_NAME"],
                    "type": row["DATA_TYPE"],
                    "nullable": row["IS_NULLABLE"],
                    "default": row["COLUMN_DEFAULT"],
                }
            )
            if row["COLUMN_KEY"] == "PRI":
                schema[tname]["primary_key"].append(row["COLUMN_NAME"])

        # Foreign keys
        for row in fk_rows:
            tname = row["TABLE_NAME"]
            if tname not in schema:
                continue
            schema[tname]["foreign_keys"].append(
                {
                    "column": row["COLUMN_NAME"],
                    "references_table": row["REFERENCED_TABLE_NAME"],
                    "references_column": row["REFERENCED_COLUMN_NAME"],
                    "constraint_name": row["CONSTRAINT_NAME"],
                }
            )

    finally:
        conn.close()

    return schema


def build_table_description(table_name: str, info: Dict) -> str:
    """
    Turn a table's schema info into a text block for the LLM.
    """
    cols = info.get("columns", [])
    pks = info.get("primary_key", [])
    fks = info.get("foreign_keys", [])

    lines: List[str] = [f"TABLE {table_name}", "Columns:"]
    for col in cols:
        lines.append(
            f"  - {col['name']} ({col['type']}, nullable={col['nullable']}, default={col['default']})"
        )

    if pks:
        lines.append(f"Primary key: {', '.join(pks)}")

    if fks:
        lines.append("Foreign keys:")
        for fk in fks:
            lines.append(
                f"  - {fk['column']} -> {fk['references_table']}({fk['references_column']}) "
                f"[{fk['constraint_name']}]"
            )

    return "\n".join(lines)


def build_all_table_descriptions(schema: Dict[str, Dict]) -> Dict[str, str]:
    """
    Returns dict: { table_name: description_text }
    """
    return {
        t: build_table_description(t, info)
        for t, info in schema.items()
    }


def run_sql(query: str, limit: int = 500) -> Tuple[List[dict], List[str]]:
    """
    Execute SQL and return (rows, columns).
    Only fetch up to 'limit' rows to avoid huge responses.
    """
    conn = get_connection()
    rows: List[dict] = []
    columns: List[str] = []

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchmany(size=limit)  # only first N rows
            if rows:
                columns = list(rows[0].keys())
    finally:
        conn.close()

    return rows, columns

def read_file(path: str):
    """
    Reads .txt or .json files.
    Returns:
        - str  (for .txt)
        - dict/list (for .json)
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    else:
        raise ValueError(f"Unsupported file type: {ext}")
