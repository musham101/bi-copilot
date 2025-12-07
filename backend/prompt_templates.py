QUERY_REWRITE_PROMPT_TEMPLATE = """You are a query rewriter. Rewrite the user's question into a clear, explicit, SQL-friendly version.

Use this database description:
{table_descriptions}

Rewrite this user question:
{user_query}

Rules for rewriting:
- Make the question unambiguous.
- Use only tables or concepts that appear in the database description.
- Expand vague terms (e.g., “last month”, “top products”, “recent orders”) into logical descriptions, but do NOT insert exact dates.
- Make implied filters, joins, metrics, and groupings explicit in natural language.
- Remove pronouns and unclear references.
- DO NOT write SQL. Only output the rewritten question in clear English.

Output ONLY the rewritten query.
"""

RELEVANT_TABLES_PROMPT_TEMPLATE = """You are an expert SQL database assistant.

Your task:
Given a REWRITTEN USER QUERY and a set of TABLE DESCRIPTIONS, identify which tables are
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
REWRITTEN USER QUERY:
{user_query}
====================

====================
TABLE DESCRIPTIONS:
{table_descriptions}
====================

Return ONLY the JSON array of table names.
"""

SQL_QUERY_PROMPT_TEMPLATE = """You are an SQL query generator with ZERO tolerance for hallucination.

Database:
- This is a MySQL relational database.
- Use MySQL syntax only.
- For time differences, you may use TIMESTAMPDIFF or comparisons with INTERVAL (e.g., WHERE t2.datetime <= t1.datetime + INTERVAL 1 DAY).
- When the query asks for customer "names", and a table with name columns is available (e.g., Person, Store), prefer using those columns instead of only IDs or account numbers.
- When multiple correct queries are possible, choose the one that is likely to be more efficient and index-friendly.

Your ONLY job is to produce a correct and PERFORMANCE-CONSCIOUS SQL query strictly based on the provided tables.

HARD RULES (must always follow):
1. Use ONLY tables and columns explicitly listed in TABLE DEFINITIONS.
2. Do NOT invent or assume any table, column, or relationship not explicitly provided.
3. If the USER QUERY cannot be satisfied with the given tables, return:
   NOT POSSIBLE WITH GIVEN TABLES
4. When joins are required, use only foreign keys or relationships explicitly implied by TABLE DEFINITIONS.
5. ALWAYS qualify columns using table aliases.
6. Prefer the minimal required set of tables.
7. SQL must be syntactically correct MySQL.

OPTIMIZATION & PERFORMANCE RULES (must also follow):
8. Prefer SELECT of only the necessary columns instead of SELECT * unless the user explicitly requests all columns.
9. Prefer SARGABLE predicates:
   - Avoid wrapping indexed columns in functions inside WHERE or JOIN conditions when an equivalent comparison using INTERVAL or range conditions is possible.
   - For time-window filters, prefer expressions like:
     t2.OrderDate > t1.OrderDate
     AND t2.OrderDate <= t1.OrderDate + INTERVAL 24 HOUR
     instead of TIMESTAMPDIFF when feasible.
10. Avoid unnecessary DISTINCT, ORDER BY, or GROUP BY if they are not required by the USER QUERY.
11. When self-joining large tables, avoid duplicate or symmetric pairs by using ordered conditions (e.g., t2.id > t1.id or t2.date > t1.date) where logically correct.
12. Push filters down as much as possible:
    - Apply restrictive WHERE conditions directly on base tables or early subqueries rather than on outer queries.
13. Use LIMIT only when the USER QUERY explicitly asks for a specific number of rows (e.g., "top 10", "first 20", "sample of 5 rows").

OUTPUT FORMAT RULES:
- Output ONLY the SQL inside a code block.
- Absolutely NO explanations.
- Absolutely NO commentary.
- Absolutely NO reasoning in the output.

====================
REWRITTEN USER QUERY:
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
