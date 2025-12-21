# 🧠 AI BI Copilot (AdventureWorks2014)

This project is an end-to-end system that:

1. Takes a **natural language query** from the user  
2. Uses **Gemini** to:
   - Select the **relevant database tables**
   - Generate a **strict, non-hallucinating SQL query**
3. Executes that SQL against the **AdventureWorks2014** MySQL database  
4. Returns the results via a **FastAPI backend**  
5. Exposes a **Streamlit frontend** for a clean, interactive UI

---

## 📁 Project Structure

```text
.
├─ README.md
├─ backend/
│  ├─ .env                           # NEW: secrets + config lives here
│  ├─ config.py                      # reads from .env using python-dotenv
│  ├─ prompt_templates.py
│  ├─ llm_utils.py
│  ├─ db_utils.py
│  ├─ sql_service.py
│  └─ main.py                        # FastAPI entrypoint
└─ frontend/
   ├─ streamlit_app_v1.py            # Streamlit UI
   └─ streamlit_app.py               # Streamlit UI
````

---

## 🚀 Backend (FastAPI)

The backend:

* Loads database credentials, Gemini API key & OpenAI API key from `.env`
* Uses **Gemini 2.5 Flash** or **gpt-4o-mini** Open to select tables + generate SQL
* Introspects the database schema via `INFORMATION_SCHEMA`
* Executes SQL and returns rows + metadata

### 1. Backend Installation

Inside the `backend/` folder:

```bash
pip install -r requirements.txt
```

---

### 2. `.env` File (Required)

Create a file named **backend/.env** with:

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
```
---

### 3. Updated `config.py` (Already Implemented)

Your backend will now load secrets like this:

```python
from dotenv import load_dotenv
load_dotenv()
```

All config comes from `.env`.

---

### 4. Run the Backend

From inside `backend/`:

```bash
uvicorn main:app --reload
```

FastAPI starts at:

```
http://localhost:8000
```

---

## 🧪 Testing Backend

### Example request

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Detect customers who placed multiple orders within 24 hours."}'
```

### Example response

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

## 🎨 Frontend (Streamlit)

The Streamlit UI allows you to:

* Enter natural language queries
* View:

  * Relevant tables
  * Generated SQL
  * Query results in a table
* Download results as CSV
* See query history (up to 10)

### 1. Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

or

```bash
streamlit run streamlit_app_v1.py
```

Open:

```
http://localhost:8501
```

---

## 🖥 How the System Works (End-to-End)

1. User enters natural language query in Streamlit
2. Streamlit sends request → FastAPI `/query`
3. FastAPI:

   * Loads schema (cached)
   * Sends request to Gemini:

     * Step 1 → **relevant tables**
     * Step 2 → **strict SQL generation**
   * Executes SQL on AdventureWorks2014
   * Returns:

     * SQL
     * Relevant tables
     * Rows + columns
4. Streamlit displays everything nicely

---

## 📌 Example Query Flow

**User Query**

> “Detect customers who placed multiple orders within 24 hours.”

Backend responds with:

* **SQL query**
* **Relevant tables:** `Customer`, `SalesOrderHeader`
* **Rows:** list of CustomerIDs

Frontend displays results instantly.

