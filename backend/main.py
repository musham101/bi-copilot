from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from sql_service import SQLService

app = FastAPI(
    title="LLM-powered SQL Assistant",
    description="Natural language to SQL on AdventureWorks2014 using Gemini + MySQL",
    version="0.1.0",
)

service = SQLService()


class QueryRequest(BaseModel):
    user_query: str


class QueryResponse(BaseModel):
    sql: str
    relevant_tables: List[str]
    columns: List[str]
    rows: List[Dict[str, Any]]


@app.post("/query", response_model=QueryResponse)
def query_db(payload: QueryRequest):
    try:
        sql_text, relevant_tables, rows, columns = service.handle_user_query(
            payload.user_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QueryResponse(
        sql=sql_text,
        relevant_tables=relevant_tables,
        columns=columns,
        rows=rows,
    )
