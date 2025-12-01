from typing import Dict, List, Tuple, Any

from db_utils import get_mysql_database_schema, build_all_table_descriptions, run_sql, read_file
from llm_utils import select_relevant_tables, generate_sql_query


class SQLService:
    def __init__(self):
        # Load schema once at startup and build textual table descriptions
        self.db_tables: Dict[str, str] = read_file("db_schema.json")

        # For relevant-table selection, we can pass the concatenated descriptions
        self.all_tables_text: str = read_file("db_description.txt")

    def handle_user_query(self, user_query: str) -> Tuple[str, List[str], List[dict], List[str]]:
        """
        Returns:
          sql_text, relevant_tables, rows, columns
        """
        # 1) Pick relevant tables
        relevant_tables = select_relevant_tables(
            user_query=user_query,
            table_descriptions=self.all_tables_text,
        )

        # 2) Build text only for these tables
        relevant_tables_text_parts = []
        for t in relevant_tables:
            desc = self.db_tables.get(t)
            if desc:
                relevant_tables_text_parts.append(desc)

        if not relevant_tables_text_parts:
            # No usable tables -> can't answer
            return "NOT POSSIBLE WITH GIVEN TABLES", [], [], []

        relevant_tables_text = "\n\n".join(relevant_tables_text_parts)

        # 3) Generate SQL
        sql_text = generate_sql_query(
            user_query=user_query,
            tables_text=relevant_tables_text,
        )

        if sql_text.strip().upper().startswith("NOT POSSIBLE WITH GIVEN TABLES"):
            # Don't run anything
            return "NOT POSSIBLE WITH GIVEN TABLES", relevant_tables, [], []

        # 4) Run SQL
        rows, columns = run_sql(sql_text)

        return sql_text, relevant_tables, rows, columns
