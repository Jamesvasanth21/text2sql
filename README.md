# 🚀 Text2SQL Analytics Engine

Text2SQL is an end-to-end conversational analytics system that converts natural language queries into SQL, executes them on structured datasets, and generates meaningful insights.

Unlike basic Text-to-SQL implementations, this project integrates:
- Schema-aware query generation using metadata
- Conversational LLM capabilities
- Automated analytics on query results

---

## 📌 Overview

This project demonstrates how to build an intelligent data interaction layer over tabular datasets.

It combines:
- **Data ingestion pipelines**
- **Metadata-driven schema understanding**
- **LLM-powered SQL generation**
- **Analytics engine for insights**

Users can interact with data using natural language queries like:

> *"Show total sales by product category in 2023"*

The system translates this into SQL, executes it, and returns results with contextual understanding.

---

## 🧠 Key Capabilities

### 🔍 Natural Language → SQL
- Converts user queries into SQL using an LLM
- Uses table and column metadata for higher accuracy

### 🧾 Metadata-Aware Intelligence
- Table descriptions and column-level metadata
- Improves semantic understanding of user queries

### 💬 Conversational Context
- Maintains context across multiple queries
- Enables follow-up questions without re-specifying details

### 📊 Analytics Engine
- Executes SQL queries
- Performs aggregations and trend analysis
- Returns structured results for further insights

### 📥 Data Pipeline
- Download datasets (Kaggle integration)
- Ingest and preprocess data
- Validate datasets before usage

---

## 🏗️ Architecture

```

User Query (Natural Language)
↓
Conversation LLM (context-aware)
↓
Metadata Layer (tables + columns)
↓
SQL Generation
↓
Query Execution (AnalyticsEngine)
↓
Result Set
↓
Insights / Response

````

---

## 📂 Repository Structure

- `AnalyticsEngine.py` — Executes SQL queries and provides analytics utilities  
- `app.py` — Entry point for running the application  
- `conversation_llm.py` — Handles LLM interaction and SQL generation  
- `config.py` — Configuration (API keys, DB connections, paths)  
- `download_data_kaggle.py` — Downloads datasets from Kaggle  
- `ingest_data.py` — Ingests CSV data into the system  
- `check_data.py` — Validates dataset integrity  
- `table_metadata.py` — Generates and manages metadata  
- `MetaData/` — Stores schema metadata  
  - `table_columns.json`  
  - `table_descriptions.json`  
- `Data/` — Sample dataset (AdventureWorks)  
- `requirements.txt` — Dependencies  
- `requirements_test.txt` — Dev/test dependencies  

---

## ⚙️ Quick Start

### Prerequisites

- Python 3.10+
- pip
- (Optional) Kaggle API credentials

---

### 1. Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
````

---

### 2. (Optional) Install Dev Dependencies

```bash
pip install -r requirements_test.txt
```

---

### 3. Configure Application

Update `config.py` with:

* LLM API key (OpenAI / Azure OpenAI)
* Database connection (if applicable)
* Data paths

---

### 4. Run the Application

```bash
python app.py
```

---

## 📊 Data & Metadata

The project uses the **AdventureWorks dataset** stored in `Data/`.

Metadata enhances SQL generation:

* `table_columns.json` → schema structure
* `table_descriptions.json` → semantic meaning

---

## 🔄 Workflow

1. Download or load dataset
2. Ingest and validate data
3. Generate metadata
4. Ask questions in natural language
5. LLM converts query → SQL
6. Analytics engine executes SQL
7. Results are returned

---

## 💡 Example Queries

* "Show total sales by category"
* "Which product has the highest revenue?"
* "Compare sales across regions"
* "What are the top 5 customers?"

---

## 🧪 Testing

```bash
pytest -q
```

Or use:

* `test.ipynb` for experimentation
* `check_data.py` for validation

---

## 🚧 Future Improvements

* Schema relationship-aware query generation
* Visualization layer (charts, dashboards)
* Multi-database support
* Query optimization
* Persistent conversational memory

---

## 🤝 Contributing

* Open issues for bugs/features
* Submit PRs with clear descriptions
* Avoid committing secrets

---

## 📜 License

No license currently specified. Consider adding MIT or Apache-2.0.

---

## 👨‍💻 Author

**James Vasanth**
Data Engineer | ML Engineer

---

## ⭐ Why This Project Matters

This project demonstrates how to combine:

* Data Engineering (ingestion, validation, schema)
* LLMs (natural language understanding)
* Analytics (query execution + insights)

to build a **next-generation data interaction system**.

```

---

