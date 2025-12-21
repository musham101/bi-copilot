import json
import time
from datetime import datetime

import requests
import pandas as pd
import streamlit as st

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="LLM SQL Assistant",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------
# SAFE UI STYLING
# ---------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Inter, system-ui, -apple-system;
}
h1, h2, h3 {
    font-weight: 600;
}
section.main {
    padding-top: 1rem;
}
section[data-testid="stSidebar"] {
    background-color: #f8f9fa;
}
textarea {
    border-radius: 10px !important;
    border: 1px solid #dcdde1 !important;
    font-size: 14px !important;
}
div.stButton > button {
    width: 100%;
    border-radius: 10px;
    padding: 0.6rem;
    font-weight: 600;
}
div.stButton > button[kind="primary"] {
    background-color: #1f6feb;
    color: white;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #1a5fd0;
}
div.stDownloadButton > button {
    background-color: #3498db;
    color: white;
    border-radius: 10px;
}
div.stDownloadButton > button:hover {
    background-color: #2980b9;
}
div[data-testid="stDataFrame"],
pre,
div[data-testid="stExpander"],
div[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("⚙️ Settings")

api_url = st.sidebar.text_input(
    "FastAPI endpoint",
    value="https://6a0876cdbf65.ngrok-free.app/query"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "- Ensure FastAPI is running\n"
    "- Ask natural language questions\n"
    "- SQL execution is read-only & safe"
)

# ---------------------------
# Session State
# ---------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------
# Header
# ---------------------------
st.title("LLM-Powered SQL Assistant")
st.caption(
    "Ask questions in natural language. The system generates and executes SQL safely."
)

# ---------------------------
# Query Input
# ---------------------------
with st.container():
    st.subheader("Ask Your Question")

    user_query = st.text_area(
        "Enter your question:",
        value="Detect customers who placed multiple orders within 24 hours.",
        height=100,
    )

    col1, col2 = st.columns([1.2, 1.8])

    with col1:
        run_button = st.button("Run Query", type="primary")

    with col2:
        show_details = st.toggle("Show SQL & metadata", value=False)

# ---------------------------
# API Helper
# ---------------------------
def call_api(api_url: str, user_query: str):
    payload = {"user_query": user_query}
    r = requests.post(api_url, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

# ---------------------------
# Run Query
# ---------------------------
if run_button:
    if not user_query.strip():
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Generating SQL and querying database..."):
            try:
                start = time.time()
                data = call_api(api_url, user_query.strip())
                latency_ms = (time.time() - start) * 1000

                sql = data.get("sql", "")
                tables = data.get("relevant_tables", [])
                rows = data.get("rows", [])
                columns = data.get("columns", [])

                df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=columns)

                # Save history
                st.session_state.history.insert(
                    0,
                    {
                        "query": user_query.strip(),
                        "sql": sql,
                        "tables": tables,
                        "rows": len(df),
                        "latency": latency_ms,
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "raw_rows": rows,
                    }
                )
                st.session_state.history = st.session_state.history[:10]

                st.success(f"Query executed successfully in {latency_ms:.0f} ms")

                # ---------------------------
                # Results
                # ---------------------------
                st.subheader(f"Results ({len(df)} rows)")
                st.dataframe(df, height=450, use_container_width=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        "⬇️ Download CSV",
                        df.to_csv(index=False).encode("utf-8"),
                        "query_results.csv",
                        "text/csv",
                    )
                with c2:
                    st.download_button(
                        "⬇️ Download JSON",
                        json.dumps(rows, indent=2).encode("utf-8"),
                        "query_results.json",
                        "application/json",
                    )

                if show_details:
                    st.markdown("### Technical Details")

                    with st.expander("Generated SQL"):
                        st.code(sql, language="sql")

                    with st.expander("Relevant Tables"):
                        st.write(", ".join(tables) if tables else "—")

                    with st.expander("Raw API Payload"):
                        st.code(json.dumps(data, indent=2), language="json")

            except Exception as e:
                st.error(str(e))

# ---------------------------
# Recent Queries (SEARCH + RESET)
# ---------------------------
if st.session_state.history:
    st.markdown("---")
    st.subheader("Recent Queries")

    search_text = st.text_input(
        "Search recent queries",
        placeholder="type to filter…"
    )

    c1, c2 = st.columns([4, 1])
    with c2:
        if st.button("Reset history"):
            st.session_state.history = []
            st.experimental_rerun()

    filtered = st.session_state.history
    if search_text.strip():
        s = search_text.lower()
        filtered = [h for h in filtered if s in h["query"].lower()]

    for i, item in enumerate(filtered):
        subtitle = f"{item['ts']} • {item['rows']} rows • {item['latency']:.0f} ms"
        with st.expander(f"{i+1}. {item['query']}\n\n{subtitle}"):
            st.code(item["query"])
            st.markdown(f"**Latency:** {item['latency']:.0f} ms")
            if item["tables"]:
                st.markdown("**Tables:** " + ", ".join(item["tables"]))
            st.code(item["sql"], language="sql")
