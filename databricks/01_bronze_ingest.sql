-- Adbri BI portfolio project: Bronze ingestion
-- Databricks SQL Warehouse / Notebook SQL
--
-- UI upload path:
-- 1. Databricks Catalog > your catalog > your schema > Volumes.
-- 2. Create a volume, for example adbri_raw.
-- 3. Upload outputs/adbri_abs_ppi_combined_long.csv to:
--    /Volumes/<catalog>/<schema>/adbri_raw/adbri_abs_ppi_combined_long.csv

CREATE CATALOG IF NOT EXISTS adbri_bi;
CREATE SCHEMA IF NOT EXISTS adbri_bi.raw;
CREATE SCHEMA IF NOT EXISTS adbri_bi.silver;
CREATE SCHEMA IF NOT EXISTS adbri_bi.gold;

USE CATALOG adbri_bi;

CREATE OR REPLACE TABLE raw.abs_ppi_long_raw
USING CSV
OPTIONS (
  path '/Volumes/adbri_bi/raw/adbri_raw/adbri_abs_ppi_combined_long.csv',
  header 'true',
  inferSchema 'true',
  encoding 'UTF-8'
);

SELECT
  dataset,
  subject,
  abs_table,
  frequency,
  COUNT(*) AS row_count,
  MIN(period_start) AS first_period,
  MAX(period_start) AS latest_period
FROM raw.abs_ppi_long_raw
GROUP BY dataset, subject, abs_table, frequency
ORDER BY dataset;
