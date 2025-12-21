**Project:** AI BI Copilot  
**Group:** Group #1  

---

## Team Member 1

### Name: Hajra Malik  
*Student ID:* MSDS24017  
*Role:* Frontend Developer (Streamlit) & Dataset Validation

### A. Contribution Table

| Category | Description of Work | Evidence / Location |
|--------|---------------------|---------------------|
| Frontend Development | Designed and implemented the user interface using Streamlit | Streamlit app files |
| User Interaction | Implemented natural-language query input and result display | Frontend scripts |
| Visualization | Integrated charts and tabular outputs returned from backend | Streamlit visualization components |
| Dataset Validation | Validated SQL queries against the database schema (ERD) | Dataset & schema files |
| Data Splits | Maintained balanced train, validation, and test splits | Dataset preparation scripts |
| UI Testing | Tested end-to-end user flow from query input to result display | Manual testing |

### B. Individual Reflection

**Biggest Contribution**  
I developed the complete Streamlit-based frontend, enabling users to interact with the BI Copilot using natural language and view SQL-driven insights through visualizations. I also contributed to validating SQL queries against the database schema to ensure dataset reliability.

**What I Learned**  
Along with frontend development, I learned how API keys are securely handled, how backend pipelines generate and execute SQL queries, and how schema consistency directly affects dataset quality and frontend reliability.

**What I Would Improve**  
I would improve the UI by adding advanced filters, better chart customization, clearer error feedback, and automate schema validation for dataset consistency.

---

## Team Member 2

### Name: Musham Ahmad Malik  
*Student ID:* MSDS24049  
*Role:* Backend, LLM & Pipeline Developer

### A. Contribution Table

| Category | Description of Work | Evidence / Location |
|--------|---------------------|---------------------|
| Backend Pipeline | Designed and implemented the end-to-end BI Copilot pipeline | Backend source code |
| Agent Logic | Implemented query rewriting, retrieval, SQL generation, and self-repair | Agent modules |
| Database Integration | Connected PostgreSQL database and handled schema retrieval | Database handlers |
| Dataset Design | Defined dataset structure and schema alignment | Dataset files |
| Evaluation Metrics | Designed metrics such as Execution Accuracy and Exact Match | Evaluation scripts |
| Safety Layer | Implemented read-only checks, query limits, and validation | Safety/validation logic |
| Experiments & Testing | Tested baseline behavior and system reliability | Scripts / notebooks |
| Architecture | Designed overall system architecture and data-to-insight flow | Architecture diagram |

### B. Individual Reflection

**Biggest Contribution**  
I implemented the complete backend and agentic pipeline, including schema retrieval, SQL generation, dataset alignment, execution, validation, and self-repair mechanisms.

**What I Learned**  
I learned that LLMs can generate syntactically correct SQL that is semantically incorrect, making execution-based dataset evaluation critical. I also gained experience coordinating backend logic with frontend and API constraints.

**What I Would Improve**  
I would improve dataset coverage, retrieval accuracy, and build a fully automated agentic benchmarking system that dynamically evaluates SQL generation against live databases.

---

## Team Member 3

### Name: Sana Ilyas  
*Student ID:* MSDS24058  
*Role:* API & Dataset Configuration Developer

### A. Contribution Table

| Category | Description of Work | Evidence / Location |
|--------|---------------------|---------------------|
| API Key Management | Created and configured API key handling for LLM access | Configuration files |
| Environment Setup | Managed environment variables and secure API usage | .env / config setup |
| Dataset Cleaning | Cleaned, normalized, and formatted SQL queries | Dataset preprocessing scripts |
| Data Validation | Ensured schema-consistent column names, types, and formats | Schema validation logic |
| Integration Support | Ensured backend services access external APIs correctly | Backend integration points |
| Testing | Verified API connectivity, dataset consistency, and error handling | Test executions |

### B. Individual Reflection

**Biggest Contribution**  
My main contribution was managing API keys and configuring secure access to external language model services, along with cleaning and validating the dataset to ensure schema-consistent SQL queries.

**What I Learned**  
I learned that even small dataset issues—such as incorrect column names or formatting—can cause major failures in query execution and evaluation. I also gained insight into how backend pipelines and frontend components depend on clean, validated data.

**What I Would Improve**  
I would automate dataset validation, add stronger logging, handle API rate limits more robustly, and integrate the dataset into an agentic evaluation framework.