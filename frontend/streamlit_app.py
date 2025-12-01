import requests
import pandas as pd
import streamlit as st

# ---------------------------
# Basic Page Config
# ---------------------------
st.set_page_config(
    page_title="LLM SQL Assistant",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------
# Sidebar Settings
# ---------------------------
st.sidebar.title("⚙️ Settings")

default_api_url = "http://localhost:8001/query"
api_url = st.sidebar.text_input("FastAPI endpoint", value=default_api_url)

st.sidebar.markdown("---")
st.sidebar.markdown("**Tips**")
st.sidebar.markdown(
    "- Make sure FastAPI is running.\n"
    "- Use natural language, e.g.:\n"
    "  - `Detect customers who placed multiple orders within 24 hours.`\n"
    "  - `Show top 10 products by total sales amount.`"
)

# ---------------------------
# Session State for History
# ---------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {query, sql, tables, row_count}


# ---------------------------
# Main Header
# ---------------------------
st.title("🧠 LLM-Powered SQL Assistant")
st.caption(
    "Ask questions in natural language. The system uses Gemini + AdventureWorks2014 to "
    "generate and execute SQL safely."
)

# ---------------------------
# Query Input Area
# ---------------------------
with st.container():
    st.subheader("📝 Ask Your Question")
    user_query = st.text_area(
        "Enter your question about the database:",
        value="Detect customers who placed multiple orders within 24 hours.",
        height=100,
        placeholder="e.g. Show total sales per year by country",
    )
    col_run, col_clear = st.columns([1, 0.4])
    with col_run:
        run_button = st.button("🚀 Run Query", type="primary")
    with col_clear:
        clear_button = st.button("🧹 Clear Results")

if clear_button:
    st.session_state.history = []
    st.experimental_rerun()

# ---------------------------
# Helper: Call FastAPI
# ---------------------------
def call_api(api_url: str, user_query: str):
    payload = {"user_query": user_query}
    resp = requests.post(api_url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ---------------------------
# Run Query
# ---------------------------
if run_button:
    if not user_query.strip():
        st.warning("Please enter a query first.")
    elif not api_url.strip():
        st.error("Please provide a valid FastAPI endpoint URL.")
    else:
        with st.spinner("Thinking, generating SQL, and querying the database..."):
            try:
                data = call_api(api_url, user_query.strip())

                sql = data.get("sql", "")
                relevant_tables = data.get("relevant_tables", [])
                columns = data.get("columns", [])
                rows = data.get("rows", [])

                # Convert rows to DataFrame for display
                df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=columns)

                # Save to history
                st.session_state.history.insert(
                    0,
                    {
                        "query": user_query.strip(),
                        "sql": sql,
                        "tables": relevant_tables,
                        "row_count": len(df),
                    },
                )

                # Limit history length
                st.session_state.history = st.session_state.history[:10]

                # Display results
                st.success("Query executed successfully!")

                # Layout: left = SQL / info, right = data table
                left_col, right_col = st.columns([1.1, 1.9])

                with left_col:
                    st.subheader("🧩 Relevant Tables")
                    if relevant_tables:
                        for t in relevant_tables:
                            st.markdown(f"- `{t}`")
                    else:
                        st.write("No tables identified or returned.")

                    st.subheader("🧾 Generated SQL")
                    if sql.strip().upper().startswith("NOT POSSIBLE WITH GIVEN TABLES"):
                        st.error("❌ Not possible with given tables.")
                        st.code(sql, language="sql")
                    else:
                        st.code(sql, language="sql")

                with right_col:
                    st.subheader(f"📊 Result Preview ({len(df)} rows)")
                    if df.empty:
                        st.info("No rows returned for this query.")
                    else:
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=450,
                        )

                        # Option to download as CSV
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="⬇️ Download results as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                        )

            except requests.exceptions.RequestException as e:
                st.error(f"Error calling API: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ---------------------------
# Query History (bottom)
# ---------------------------
if st.session_state.history:
    st.markdown("---")
    st.subheader("🕒 Recent Queries")

    for i, item in enumerate(st.session_state.history):
        with st.expander(f"{i+1}. {item['query']}"):
            st.markdown(f"**Row count:** `{item['row_count']}`")
            if item["tables"]:
                st.markdown("**Relevant tables:** " + ", ".join(f"`{t}`" for t in item["tables"]))
            st.markdown("**Generated SQL:**")
            st.code(item["sql"], language="sql")