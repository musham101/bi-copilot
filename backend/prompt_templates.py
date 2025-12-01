RALEVANT_TABLES_PROMPT_TEMPLATE = """You are an expert SQL database assistant.

Your task:
Given a USER QUERY and a set of TABLE DESCRIPTIONS, identify which tables are
relevant for answering the user query.

Instructions:
- Use only the tables described below.
- Select the smallest set of tables that fully answer the query.
- Prefer highly relevant tables over loosely related ones.
- DO NOT invent tables that are not provided.
- Return ONLY a JSON array of table names, like:
  ["Customer", "SalesOrderHeader"]

Output format:
- No explanation.
- No commentary.
- Only a JSON list of table names.

====================
USER QUERY:
{user_query}
====================

====================
TABLE DESCRIPTIONS:
{table_descriptions}
====================

Return ONLY the JSON array of table names.
"""

SQL_QUERY_PROMPT_TEMPLATE = """You are an SQL query generator with ZERO tolerance for hallucination.

Your ONLY job is to produce a correct SQL query strictly based on the provided tables.

HARD RULES (must always follow):
1. Use ONLY tables and columns explicitly listed in TABLE DEFINITIONS.
2. Do NOT invent or assume any table, column, or relationship not explicitly provided.
3. If the USER QUERY cannot be satisfied with the given tables, return:
   NOT POSSIBLE WITH GIVEN TABLES
4. When joins are required, use only foreign keys explicitly listed.
5. ALWAYS qualify columns using table aliases.
6. Prefer the minimal required set of tables.
7. SQL must be syntactically correct and optimized.

OUTPUT FORMAT RULES:
- Output ONLY the SQL inside a code block.
- Absolutely NO explanations.
- Absolutely NO commentary.
- Absolutely NO reasoning in the output.

====================
USER QUERY:
{user_query}
====================

====================
TABLE DEFINITIONS:
{tables}
====================

Return ONLY the SQL query in a code block.
If impossible, return exactly:
NOT POSSIBLE WITH GIVEN TABLES
"""
