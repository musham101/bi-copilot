import json
import os
from typing import List

from dotenv import load_dotenv
load_dotenv()

from prompt_templates import (
    RELEVANT_TABLES_PROMPT_TEMPLATE,
    SQL_QUERY_PROMPT_TEMPLATE,
    QUERY_REWRITE_PROMPT_TEMPLATE
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

LLM_PROVIDER = None
client = None

if GEMINI_API_KEY:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    generation_config = types.GenerateContentConfig(temperature=0.0)
    LLM_PROVIDER = "gemini"

elif OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    LLM_PROVIDER = "openai"

if not LLM_PROVIDER:
    raise RuntimeError("No LLM provider found in .env. Provide either GEMINI_API_KEY or OPENAI_API_KEY.")


def llm_generate(prompt: str) -> str:
    """
    Return raw text output from whichever LLM provider is active.
    - Gemini
    - OpenAI
    """
    if LLM_PROVIDER == "gemini":
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=generation_config,
        )
        return response.text.strip()

    elif LLM_PROVIDER == "openai":
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()

    else:
        raise RuntimeError("Invalid LLM provider configured.")

def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[-1].strip().startswith("```"):
            lines = lines[1:-1]  # remove both fences
        else:
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text

def select_relevant_tables(user_query: str, table_descriptions: str) -> List[str]:
    prompt = RELEVANT_TABLES_PROMPT_TEMPLATE.format(
        user_query=user_query,
        table_descriptions=table_descriptions,
    )

    raw = llm_generate(prompt)
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

    text = llm_generate(prompt)
    text = _strip_code_fences(text)

    # special case handling
    if text.strip().upper().startswith("NOT POSSIBLE WITH GIVEN TABLES"):
        return "NOT POSSIBLE WITH GIVEN TABLES"

    return text.strip()

def rewrite_user_query(user_query: str, table_descriptions: str) -> str:
    prompt = QUERY_REWRITE_PROMPT_TEMPLATE.format(
        user_query=user_query,
        table_descriptions=table_descriptions,
    )

    # Call your LLM
    rewritten = llm_generate(prompt)

    # Remove code fences if model returns ```text```
    rewritten = _strip_code_fences(rewritten)

    # Optional special-case handling
    if rewritten.strip().upper().startswith("NOT POSSIBLE WITH GIVEN TABLES"):
        return "NOT POSSIBLE WITH GIVEN TABLES"

    return rewritten.strip()