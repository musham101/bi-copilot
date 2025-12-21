# AI BI Copilot (AdventureWorks2014)

An end-to-end **LLM-powered BI Copilot** that:

1. Takes a natural language query
2. Uses LLMs (Gemini / OpenAI) to:

   * Select relevant database tables
   * Generate a strict, schema-grounded SQL query
3. Executes SQL on the AdventureWorks2014 (MySQL) database
4. Serves results via a FastAPI backend
5. Provides a Streamlit frontend for interactive querying
6. Includes an evaluation notebook that benchmarks the system using `val.csv` and `test.csv`

---

## Project Structure

```text
.
├─ README.md
├─ data/
│  ├─ val.csv                         # Validation set for tuning
│  └─ test.csv                        # Held-out evaluation set
└─ src/
   ├─ backend/
   │  ├─ .env                         # Backend secrets + config
   │  ├─ config.py                    # Loads env vars via python-dotenv
   │  ├─ prompt_templates.py
   │  ├─ llm_utils.py
   │  ├─ db_utils.py
   │  ├─ sql_service.py
   │  └─ main.py                      # FastAPI entrypoint
   ├─ frontend/
   │  ├─ streamlit_app.py             # Streamlit UI (primary)
   │  └─ streamlit_app_v1.py
   └─ notebooks/
      ├─ .env                         # Notebook secrets (separate from backend)
      └─ evalutate_system.ipynb       # Evaluation notebook (FastAPI + OpenAI judge)
```

---

## Backend (FastAPI)

The backend is responsible for:

* Loading credentials and API keys from `src/backend/.env`
* Introspecting schema via `INFORMATION_SCHEMA` (cached)
* LLM step 1: table selection
* LLM step 2: SQL generation
* Executing SQL on AdventureWorks2014 and returning:

  * generated SQL
  * selected tables
  * returned columns
  * result rows

### Supported LLMs

* Gemini 2.5 Flash
* OpenAI models (e.g., gpt-4o-mini, gpt-5-mini)

---

### Install backend dependencies

```bash
pip install -r requirements.txt
```

---

### Backend environment variables

Create `src/backend/.env`:

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
# Optional DB config:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=...
# DB_NAME=AdventureWorks2014
```

---

### Run the backend

```bash
cd src/backend
uvicorn main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

---

## API Testing

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Detect customers who placed multiple orders within 24 hours."}'
```

Example response:

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

The Streamlit UI supports:

* Natural language query input
* Viewing:

  * relevant tables
  * generated SQL
  * results table
* CSV download
* Query history (up to 10)

### Run the frontend

```bash
cd src/frontend
streamlit run streamlit_app.py
```

(or)

```bash
streamlit run streamlit_app_v1.py
```

Open:

```
http://localhost:8501
```

---

## End-to-End Flow

1. User enters a query in Streamlit
2. Streamlit sends request to FastAPI (`POST /query`)
3. FastAPI:

   * loads cached schema
   * selects relevant tables via LLM
   * generates strict SQL
   * executes SQL
4. Response includes SQL, tables, columns, and rows
5. Streamlit renders results

---

## Evaluation (Notebook)

Evaluation is performed in:

```
src/notebooks/evalutate_system.ipynb
```

The notebook:

* Sends each user query to the running FastAPI backend
* Compares predicted SQL against gold SQL using:

  * Exact match
  * Normalized exact match
  * Token-level F1
  * Keyword F1
  * Edit similarity
* Optionally uses an OpenAI judge (Responses API) for semantic equivalence scoring (0–5)

---

### Notebook environment variables

Create `src/notebooks/.env`:

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

This allows evaluation to run independently from backend configuration.

---

### Dataset path configuration

Dataset files are located at:

```text
data/val.csv
data/test.csv
```

From `src/notebooks/`, set in the notebook:

```python
DATASET_DIR = "../../data"
```

---

### Running evaluation

1. Start the backend:

   ```bash
   uvicorn main:app --reload
   ```
2. Open and run all cells in `evalutate_system.ipynb`
3. Evaluation outputs are saved as:

   * `eval_results_<timestamp>.csv`
   * `eval_summary_<timestamp>.json`

---

## Notes on OpenAI Judge Model

The notebook defaults to:

```python
OPENAI_MODEL = "gpt-4o-mini"
```

Ensure the selected model is available in your OpenAI account.
