# AI BI Copilot (AdventureWorks2014)

This project is an end-to-end **LLM-powered Business Intelligence Copilot** that:

1. Takes a **natural language query** from the user
2. Uses **LLMs (Gemini / OpenAI)** to:

   * Select the **relevant database tables**
   * Generate a **strict, non-hallucinating SQL query**
3. Executes that SQL against the **AdventureWorks2014 (MySQL)** database
4. Returns results via a **FastAPI backend**
5. Exposes a **Streamlit frontend** for an interactive UI
6. Supports **offline evaluation** using labeled datasets (`test.csv`, `val.csv`)

---

## Project Structure

```text
.
├─ README.md
├─ data/
│  ├─ test.csv              # Evaluation dataset (held-out)
│  └─ val.csv               # Validation dataset
└─ src/
   ├─ backend/
   │  ├─ .env               # Secrets & configuration
   │  ├─ config.py          # Loads env vars via python-dotenv
   │  ├─ prompt_templates.py
   │  ├─ llm_utils.py
   │  ├─ db_utils.py
   │  ├─ sql_service.py
   │  └─ main.py            # FastAPI entrypoint
   └─ frontend/
      ├─ streamlit_app.py   # Primary Streamlit UI
      └─ streamlit_app_v1.py
```

---

## Backend (FastAPI)

The backend is responsible for:

* Loading credentials from `.env`
* Schema introspection using `INFORMATION_SCHEMA`
* LLM-based **table selection + SQL generation**
* SQL execution on AdventureWorks2014
* Returning rows, columns, and metadata

### Supported LLMs

* **Gemini 2.5 Flash**
* **gpt-4o-mini**

---

### 1. Backend Installation

From the project root:

```bash
pip install -r requirements.txt
```

---

### 2. `.env` File (Required)

Create **`src/backend/.env`**:

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

All secrets are loaded centrally via `config.py`.

---

### 3. Config Loading (Already Implemented)

```python
from dotenv import load_dotenv
load_dotenv()
```

No hardcoded secrets anywhere in the codebase.

---

### 4. Run the Backend

```bash
cd src/backend
uvicorn main:app --reload
```

FastAPI will be available at:

```
http://localhost:8000
```

---

## Backend API Testing

### Example Request

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Detect customers who placed multiple orders within 24 hours."}'
```

### Example Response

```json
{
  "sql": "SELECT ...",
  "relevant_tables": ["Customer", "SalesOrderHeader"],
  "columns": ["CustomerID"],
  "rows": [
    { "CustomerID": 11300 },
    { "CustomerID": 11176 }
  ]
}
```

---

## Frontend (Streamlit)

The Streamlit UI allows users to:

* Enter natural language queries
* View:

  * Selected tables
  * Generated SQL
  * Query results (tabular)
* Download results as CSV
* Browse recent query history (up to 10)

---

### Run the Streamlit App

From the project root:

```bash
cd src/frontend
streamlit run streamlit_app.py
```

(or `streamlit_app_v1.py`)

Open in browser:

```
http://localhost:8501
```

---

## End-to-End System Flow

1. User enters a query in **Streamlit**
2. Streamlit → `POST /query`
3. FastAPI:

   * Loads cached schema
   * LLM step 1 → relevant tables
   * LLM step 2 → strict SQL
   * Executes SQL
4. Response returned:

   * SQL
   * Tables
   * Columns
   * Rows
5. Streamlit renders everything interactively

---

## Evaluation & Benchmarking

The `data/` directory contains labeled datasets used to **evaluate system quality**:

```text
data/
├─ val.csv     # Used during development & tuning
└─ test.csv    # Final evaluation set
```

These datasets are used to measure:

* SQL exact match
* Normalized SQL match
* Token-level F1
* Keyword F1
* Execution correctness
* LLM judge scores (optional)

> **Important:**
> `test.csv` is never used during prompt or system tuning.

---

## Example Query

**User Input**

> “Detect customers who placed multiple orders within 24 hours.”

**System Output**

* **Relevant Tables:** `Customer`, `SalesOrderHeader`
* **Generated SQL:** Strict, executable SQL
* **Result:** List of CustomerIDs

Displayed instantly in the frontend.
