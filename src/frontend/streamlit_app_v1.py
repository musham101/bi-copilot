import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st


# ============================================================
# Page Config + Global Styling
# ============================================================
st.set_page_config(
    page_title="LLM SQL Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Subtle, clean styling (no external CSS files)
st.markdown(
    """
<style>
/* Make header spacing nicer */
.block-container { padding-top: 1.3rem; }

/* Slightly larger buttons */
.stButton button { border-radius: 12px; padding: 0.6rem 1rem; }

/* Code blocks: rounded + slightly darker bg */
pre { border-radius: 14px !important; }

/* Dataframe container polish */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }

/* Sidebar titles spacing */
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

/* Expander polish */
div[data-testid="stExpander"] details { border-radius: 14px; }

/* Metric cards spacing */
[data-testid="stMetric"] { padding: 0.25rem 0.25rem 0.75rem 0.25rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Helpers
# ============================================================
DEFAULT_API_URL = "https://6a0876cdbf65.ngrok-free.app/query"
DEFAULT_QUERY = "Detect customers who placed multiple orders within 24 hours."

SAMPLE_QUERIES = [
    "Show top 10 products by total sales amount.",
    "List customers who have never placed an order.",
    "Total sales per year grouped by country.",
    "Which salespersons have the highest revenue?",
    "Find customers who placed multiple orders within 24 hours.",
    "Average order value by month for the last 2 years.",
]

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_df(rows: List[Dict[str, Any]], columns: List[str]) -> pd.DataFrame:
    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame(columns=columns or [])

def is_not_possible_sql(sql: str) -> bool:
    return sql.strip().upper().startswith("NOT POSSIBLE WITH GIVEN TABLES")

@st.cache_data(show_spinner=False, ttl=10)  # tiny cache to avoid double-hit on reruns
def call_api(api_url: str, user_query: str) -> Dict[str, Any]:
    payload = {"user_query": user_query}
    resp = requests.post(api_url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()

def ping_api(api_url: str) -> Tuple[bool, str]:
    """
    Non-invasive “ping”: we do a short request with a harmless query.
    If your backend supports /health, replace this with a GET to /health.
    """
    try:
        t0 = time.time()
        _ = requests.post(api_url, json={"user_query": "Show 1 row."}, timeout=6)
        dt = (time.time() - t0) * 1000
        if _.status_code >= 200 and _.status_code < 500:
            return True, f"Reachable ({dt:.0f} ms)"
        return False, f"Status {_.status_code}"
    except Exception as e:
        return False, str(e)

def push_history(item: Dict[str, Any], limit: int = 12) -> None:
    st.session_state.history.insert(0, item)
    st.session_state.history = st.session_state.history[:limit]


# ============================================================
# Session State
# ============================================================
if "history" not in st.session_state:
    # Each item: {ts, query, sql, tables, row_count, latency_ms}
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None  # store most recent result payload for reuse

if "user_query" not in st.session_state:
    st.session_state.user_query = DEFAULT_QUERY

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL


# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.title("⚙️ Settings")

    api_url = st.text_input(
        "FastAPI endpoint",
        value=st.session_state.api_url,
        placeholder="http://localhost:8001/query",
        help="Your Streamlit app will POST to this endpoint with { user_query: ... }",
    )
    st.session_state.api_url = api_url

    c1, c2 = st.columns([1, 1])
    with c1:
        test_btn = st.button("🔌 Test API", use_container_width=True)
    with c2:
        clear_history_btn = st.button("🧹 Clear", use_container_width=True)

    if test_btn:
        ok, msg = ping_api(api_url.strip())
        if ok:
            st.success(f"API: {msg}")
        else:
            st.error(f"API not reachable: {msg}")

    if clear_history_btn:
        st.session_state.history = []
        st.session_state.last_result = None
        st.toast("Cleared.", icon="🧹")

    st.markdown("---")

    st.subheader("💡 Examples")
    st.caption("Click to insert into the query box.")
    for q in SAMPLE_QUERIES:
        if st.button(f"➕ {q}", use_container_width=True):
            st.session_state.user_query = q
            st.toast("Inserted example query.", icon="✅")

    st.markdown("---")
    st.subheader("🔒 Notes")
    st.write(
        "- Make sure FastAPI is running.\n"
        "- Use natural language queries.\n"
        "- If the backend rejects unsafe SQL, you’ll see an error."
    )


# ============================================================
# Main Header
# ============================================================
top_left, top_right = st.columns([1.6, 1.0])

with top_left:
    st.title("🧠 LLM-Powered SQL Assistant")
    st.caption(
        "Ask questions in natural language. The system uses Gemini + AdventureWorks2014 to "
        "generate and execute SQL safely."
    )

with top_right:
    # Quick glance stats from history
    total_runs = len(st.session_state.history)
    last_rows = st.session_state.history[0]["row_count"] if total_runs else 0
    last_latency = st.session_state.history[0].get("latency_ms", None) if total_runs else None

    m1, m2, m3 = st.columns(3)
    m1.metric("Runs", total_runs)
    m2.metric("Last rows", last_rows)
    m3.metric("Latency", f"{last_latency:.0f} ms" if last_latency is not None else "—")


st.markdown("")


# ============================================================
# Query Composer
# ============================================================
with st.container(border=True):
    st.subheader("📝 Ask your question")

    user_query = st.text_area(
        "Query",
        key="user_query",
        height=120,
        placeholder="e.g. Show total sales per year by country",
        label_visibility="collapsed",
    )

    a, b, c, d = st.columns([1.1, 1.1, 1.1, 1.7])

    with a:
        run_button = st.button("🚀 Run Query", type="primary", use_container_width=True)
    with b:
        reset_button = st.button("↩️ Reset", use_container_width=True)
    with c:
        explain_toggle = st.toggle("Show details", value=True)
    with d:
        st.caption("Tip: Keep questions specific (tables, time ranges, top N, etc.)")

    if reset_button:
        st.session_state.user_query = DEFAULT_QUERY
        st.toast("Reset query.", icon="↩️")


# ============================================================
# Execute Query
# ============================================================
error_box = st.empty()

if run_button:
    error_box.empty()

    if not user_query.strip():
        error_box.warning("Please enter a query first.")
    elif not api_url.strip():
        error_box.error("Please provide a valid FastAPI endpoint URL.")
    else:
        with st.spinner("Thinking → generating SQL → querying the database..."):
            try:
                t0 = time.time()
                data = call_api(api_url.strip(), user_query.strip())
                latency_ms = (time.time() - t0) * 1000

                sql = data.get("sql", "") or ""
                relevant_tables = data.get("relevant_tables", []) or []
                columns = data.get("columns", []) or []
                rows = data.get("rows", []) or []

                df = safe_df(rows, columns)

                st.session_state.last_result = {
                    "query": user_query.strip(),
                    "sql": sql,
                    "tables": relevant_tables,
                    "columns": columns,
                    "rows": rows,
                    "latency_ms": latency_ms,
                    "ts": now_str(),
                }

                push_history(
                    {
                        "ts": now_str(),
                        "query": user_query.strip(),
                        "sql": sql,
                        "tables": relevant_tables,
                        "row_count": len(df),
                        "latency_ms": latency_ms,
                    }
                )

                st.toast("Query executed.", icon="✅")

            except requests.exceptions.Timeout:
                error_box.error("⏱️ API timed out. Try again or increase backend timeout.")
            except requests.exceptions.ConnectionError:
                error_box.error("🔌 Could not connect to the API. Is FastAPI running and reachable?")
            except requests.exceptions.HTTPError as e:
                # Attempt to show backend error detail if present
                detail = None
                try:
                    detail = e.response.json()
                except Exception:
                    detail = e.response.text if e.response is not None else None

                error_box.error(f"API returned an error: {e}")
                if detail:
                    with st.expander("View error detail"):
                        st.code(
                            json.dumps(detail, indent=2) if isinstance(detail, (dict, list)) else str(detail),
                            language="json",
                        )
            except Exception as e:
                error_box.error(f"Unexpected error: {e}")


# ============================================================
# Result Viewer
# ============================================================
result = st.session_state.last_result

if result:
    sql = result["sql"]
    tables = result["tables"]
    columns = result["columns"]
    rows = result["rows"]
    df = safe_df(rows, columns)
    latency_ms = result.get("latency_ms", None)

    st.markdown("")
    st.subheader("📌 Results")

    # Top summary row
    s1, s2, s3, s4 = st.columns([1.2, 1.0, 1.0, 1.8])
    s1.metric("Rows", len(df))
    s2.metric("Tables", len(tables))
    s3.metric("Latency", f"{latency_ms:.0f} ms" if latency_ms is not None else "—")
    s4.caption(f"Last run: **{result.get('ts', '—')}**")

    tab1, tab2, tab3 = st.tabs(["📊 Data", "🧾 SQL", "🧠 Metadata"])

    with tab1:
        if df.empty:
            st.info("No rows returned for this query.")
        else:
            st.dataframe(df, use_container_width=True, height=520)

            cdl, cdr = st.columns([1.2, 1.0])
            with cdl:
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with cdr:
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json.dumps(rows, indent=2).encode("utf-8"),
                    file_name="query_results.json",
                    mime="application/json",
                    use_container_width=True,
                )

    with tab2:
        if is_not_possible_sql(sql):
            st.error("❌ Not possible with given tables.")
        st.code(sql or "-- (empty)", language="sql")

        if explain_toggle:
            with st.expander("Copy-friendly SQL (plain text)"):
                st.text(sql or "")

    with tab3:
        st.write("**Relevant tables**")
        if tables:
            st.write(" ".join([f"`{t}`" for t in tables]))
        else:
            st.caption("No tables identified or returned.")

        st.write("**Payload (debug)**")
        with st.expander("View full response JSON"):
            st.code(json.dumps(result, indent=2), language="json")


# ============================================================
# History
# ============================================================
if st.session_state.history:
    st.markdown("---")
    st.subheader("🕒 Recent Queries")

    # Quick filter/search
    q_filter = st.text_input("Search history", placeholder="type to filter…")
    filtered = st.session_state.history
    if q_filter.strip():
        qf = q_filter.strip().lower()
        filtered = [h for h in filtered if qf in h["query"].lower()]

    for i, item in enumerate(filtered):
        title = f"{i+1}. {item['query']}"
        subtitle = f"{item.get('ts','—')} • {item['row_count']} rows • {item.get('latency_ms', 0):.0f} ms"
        with st.expander(f"{title}\n\n{subtitle}"):
            cols = st.columns([1.2, 2.0])
            with cols[0]:
                st.write("**Relevant tables**")
                if item["tables"]:
                    st.write(", ".join([f"`{t}`" for t in item["tables"]]))
                else:
                    st.caption("—")

            with cols[1]:
                st.write("**Generated SQL**")
                st.code(item["sql"], language="sql")