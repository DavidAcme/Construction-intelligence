# Adbri Construction Intelligence

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Databricks](https://img.shields.io/badge/Databricks-SQL-red)](https://www.databricks.com/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Star%20Schema-yellow)](https://powerbi.microsoft.com/)
[![RAG](https://img.shields.io/badge/RAG-LangChain%20%2B%20FAISS-green)](https://python.langchain.com/)

An end-to-end BI and AI portfolio project for construction market analysis.
It transforms Australian Bureau of Statistics time-series workbooks into a
Databricks-style medallion model, a Power BI market dashboard, and a local
LangChain/RAG assistant backed by Ollama.

## Business Goal

Adbri is a building materials company, so this BI project focuses on two market signals:

- Demand signal: South Australia building approvals.
- Cost pressure signal: construction and house construction Producer Price Indexes.

The final Power BI report should answer:

- Is SA construction demand rising or softening?
- Are Adelaide construction input costs increasing?
- Which building types, sectors, or regions are driving the change?
- Can the data pipeline be trusted?

## Architecture

```text
ABS Excel workbooks
  -> Python wide-to-long transformation
  -> Databricks Bronze / Silver / Gold SQL
  -> Power BI star schema and DAX
  -> LangChain + multilingual embeddings + FAISS + Ollama
```

## Repository Structure

| Path | Purpose |
|---|---|
| `scripts/extract_abs_excel_to_csv.py` | Converts the four ABS Excel files from wide format to tidy long CSV |
| `outputs/adbri_abs_ppi_combined_long.csv` | Combined upload file for Databricks |
| `databricks/01_bronze_ingest.sql` | Bronze table ingestion from Databricks Volume |
| `databricks/02_silver_gold_model.sql` | Typed Silver table and Gold star schema |
| `databricks/03_quality_checks.sql` | SQL checks for row counts, duplicates, nulls, and latest indicators |
| `powerbi/power_bi_model_and_dax.md` | Power BI relationships, DAX measures, and report pages |
| `docs/data_dictionary.md` | Source and field definitions, including the Power BI-safe `series_key` |
| `docs/skills_learning_plan_cn.md` | Chinese learning/interview plan for SQL, Databricks, Power BI, Python, Fabric, Azure |
| `ai_assistant/` | Local bilingual RAG assistant using FAISS, LangChain, and Ollama |

## Source Data

The raw ABS workbooks are not committed. Place them in `source_data/`:

- `Building_Approvals_SA_Table04.xlsx`
- `Building_Approvals_SA_Table15.xlsx`
- `PPI_Construction_Output_Table17.xlsx`
- `PPI_House_Construction_Input_Table18.xlsx`

Alternatively, pass another folder with `--source-dir` or set
`ADBRI_SOURCE_DIR`.

## Run Extraction

```powershell
python .\scripts\extract_abs_excel_to_csv.py --source-dir .\source_data
```

Expected output:

| CSV | Rows |
|---|---:|
| `building_approvals_sa_table04.csv` | 7,182 |
| `building_approvals_sa_table15.csv` | 9,382 |
| `ppi_construction_output_table17.csv` | 4,980 |
| `ppi_house_construction_input_table18.csv` | 22,182 |
| `adbri_abs_ppi_combined_long.csv` | 43,726 |

## Databricks Workflow

1. Upload `outputs/adbri_abs_ppi_combined_long.csv` to a Databricks Volume.
2. Run `databricks/01_bronze_ingest.sql`.
3. Run `databricks/02_silver_gold_model.sql`.
4. Run `databricks/03_quality_checks.sql`.
5. Connect Power BI to `gold.fact_market_indicators`, `gold.dim_series`, and `gold.dim_date`.

## Power BI Workflow

1. Use Azure Databricks connector.
2. Build relationships from fact to date and series dimensions.
3. Add the DAX measures in `powerbi/power_bi_model_and_dax.md`.
4. Create four report pages:
   - Executive Market Pulse
   - Building Approvals Demand
   - Construction Cost Pressure
   - Data Quality and Lineage

## Local RAG Assistant

Install dependencies:

```powershell
python -m pip install -r .\ai_assistant\requirements-rag.txt
```

Ensure Ollama is running with `qwen2.5:7b`, then build the knowledge index:

```powershell
python .\ai_assistant\01_prepare_documents.py
python .\ai_assistant\02_build_vector_index.py
```

Run the local assistant:

```powershell
cd .\ai_assistant
python .\04_rag_chat.py
```

LangChain LCEL example:

```powershell
python .\05_langchain_rag.py "Did South Australia demand recover in 2025?"
```

## Key Findings

- Selected South Australia approvals recovered from approximately 24,474 in
  2024 to 29,623 in 2025.
- March 2026 selected approvals were approximately 8.6% above March 2025.
- Adelaide house construction input PPI rose approximately 3.7% year over year.
- South Australia building construction output PPI rose approximately 3.8%.

These findings suggest recovering construction demand alongside persistent
cost and output-price pressure.
