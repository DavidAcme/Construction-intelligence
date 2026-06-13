# Adbri BI Analyst 六项技能学习路线

目标岗位关键词：Databricks, Power BI, SQL, Python, Fabric, Azure。这个项目要讲成一个端到端 BI delivery，而不是只会做图。

## 1. SQL

必须掌握：

- `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`
- `JOIN`: fact/dimension star schema
- window functions: `LAG`, `LEAD`, `ROW_NUMBER`, moving average
- CTE: 把复杂逻辑拆开
- data quality checks: duplicate grain, null checks, row count reconciliation

本项目讲法：

> I used SQL to transform ABS time-series data into a clean star schema, added period-over-period and annual change calculations with window functions, and wrote data quality checks to validate row counts, nulls, and duplicate grain.

## 2. Databricks

必须掌握：

- Workspace, Notebook, SQL Warehouse
- Catalog, Schema, Volume, Delta table
- Bronze/Silver/Gold medallion architecture
- Databricks SQL endpoint for Power BI
- `OPTIMIZE` and `ZORDER` basics

本项目讲法：

> I uploaded raw ABS/PPI data into a Databricks Volume, created a Bronze table from CSV, transformed it into a typed Silver fact table, then published Gold dimension and fact tables for Power BI consumption.

## 3. Power BI

必须掌握：

- Star schema modelling
- relationships and filter direction
- DAX measures, not just calculated columns
- report pages for executive summary, operational detail, data quality
- slicers, tooltips, conditional formatting
- Import vs DirectQuery trade-offs

本项目讲法：

> I connected Power BI to Databricks Gold tables, built a star schema, created DAX measures for latest value, period change, and annual change, then designed report pages for demand, cost pressure, and data quality.

## 4. Python

必须掌握：

- reading Excel/CSV
- cleaning messy headers
- reshaping wide data to long data
- basic validation and row counts
- writing reproducible scripts

本项目讲法：

> The ABS workbooks came in a wide time-series format, so I wrote a Python extraction script to parse series metadata and reshape each workbook into a tidy long CSV suitable for Databricks ingestion.

## 5. Microsoft Fabric

必须掌握：

- Lakehouse, Warehouse, Dataflow Gen2, Notebook
- OneLake concept
- Direct Lake vs Import vs DirectQuery
- relationship between Fabric and Power BI semantic models

本项目讲法：

> The same pattern can be implemented in Microsoft Fabric using OneLake/Lakehouse as the storage layer, Fabric Dataflow or Notebook for transformation, and a Power BI semantic model over Gold tables.

## 6. Azure

必须掌握：

- Azure Data Lake Storage Gen2
- Entra ID basics
- Key Vault basics
- Azure Databricks workspace
- cost/security awareness: managed identity, least privilege, workspace access

本项目讲法：

> In a production Azure setup, I would land files in ADLS Gen2, secure secrets through Key Vault or managed identity, run transformations in Azure Databricks, and serve curated Delta tables to Power BI.

## 30-Day Practice Plan

| Week | Focus | Output |
|---|---|---|
| 1 | SQL + data modelling | Recreate Bronze/Silver/Gold tables and explain the grain |
| 2 | Databricks | Run ingestion, build Delta tables, perform quality checks |
| 3 | Power BI | Build all report pages and DAX measures |
| 4 | Fabric + Azure + interview | Rebuild the architecture diagram and practise project story |

## Interview Project Story

Use this 60-second version:

> I built a BI project for Adbri-style building materials market analysis using ABS building approvals and construction PPI data. The raw Excel files had ABS metadata rows and wide time-series columns, so I used Python to reshape them into tidy long format. In Databricks I created Bronze, Silver, and Gold layers, with quality checks for row counts, duplicates, and nulls. The Gold model was a star schema with date, series, and market indicator fact tables. In Power BI I designed pages for SA construction demand, Adelaide cost pressure, executive market pulse, and data quality. The project demonstrates SQL, Databricks, Power BI, Python, and how the same architecture can extend into Azure or Fabric.
