import json
from typing import List

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL
from prompt_templates import (
    RALEVANT_TABLES_PROMPT_TEMPLATE,
    SQL_QUERY_PROMPT_TEMPLATE,
)

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

client = genai.Client(api_key=GEMINI_API_KEY)

generation_config = types.GenerateContentConfig(
    temperature=0.0,
)


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        # remove first fence line
        lines = text.splitlines()
        # drop first line and any trailing fence
        if len(lines) >= 2 and lines[-1].strip().startswith("```"):
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


def select_relevant_tables(user_query: str, table_descriptions: str) -> List[str]:
    prompt = RALEVANT_TABLES_PROMPT_TEMPLATE.format(
        user_query=user_query,
        table_descriptions=table_descriptions,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt],
        config=generation_config,
    )

    raw = response.text.strip()
    raw = _strip_code_fences(raw)
    try:
        tables = json.loads(raw)
        if not isinstance(tables, list):
            raise ValueError("Expected JSON list of table names")
        return [str(t).strip() for t in tables]
    except Exception as e:
        raise RuntimeError(f"Failed to parse relevant tables JSON: {e}\nRaw: {raw}") from e


def generate_sql_query(user_query: str, tables_text: str) -> str:
    prompt = SQL_QUERY_PROMPT_TEMPLATE.format(
        user_query=user_query,
        tables=tables_text,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt],
        config=generation_config,
    )

    text = response.text or ""
    text = _strip_code_fences(text)

    # handle NOT POSSIBLE case as-is
    if text.strip().upper().startswith("NOT POSSIBLE WITH GIVEN TABLES"):
        return "NOT POSSIBLE WITH GIVEN TABLES"

    return text.strip()
