-- Adbri BI portfolio project: Silver and Gold semantic model
USE CATALOG adbri_bi;

CREATE OR REPLACE TABLE silver.fact_abs_ppi_series AS
SELECT
  source_file,
  dataset,
  COALESCE(series_key, CONCAT(dataset, '|', series_id)) AS series_key,
  subject,
  abs_table,
  CAST(period_start AS DATE) AS period_start,
  CAST(year AS INT) AS year,
  CAST(quarter AS INT) AS quarter,
  CAST(month AS INT) AS month,
  CAST(value AS DOUBLE) AS value,
  series_id,
  series_description,
  unit,
  series_type,
  data_type,
  frequency,
  CAST(collection_month AS INT) AS collection_month,
  CAST(series_start AS DATE) AS series_start,
  CAST(series_end AS DATE) AS series_end,
  CAST(no_obs AS INT) AS no_obs,
  metric,
  category_1,
  category_2,
  category_3,
  category_4,
  category_5,
  region,
  city,
  current_timestamp() AS loaded_at
FROM raw.abs_ppi_long_raw
WHERE period_start IS NOT NULL
  AND value IS NOT NULL;

CREATE OR REPLACE TABLE gold.dim_date AS
SELECT DISTINCT
  period_start AS date_key,
  year,
  quarter,
  month,
  date_format(period_start, 'yyyy-MM') AS year_month,
  CONCAT(CAST(year AS STRING), '-Q', CAST(quarter AS STRING)) AS year_quarter
FROM silver.fact_abs_ppi_series;

CREATE OR REPLACE TABLE gold.dim_series AS
SELECT DISTINCT
  series_key,
  series_id,
  dataset,
  subject,
  abs_table,
  series_description,
  unit,
  series_type,
  data_type,
  frequency,
  metric,
  category_1,
  category_2,
  category_3,
  category_4,
  category_5,
  region,
  city
FROM silver.fact_abs_ppi_series;

CREATE OR REPLACE TABLE gold.fact_market_indicators AS
SELECT
  period_start AS date_key,
  series_key,
  series_id,
  dataset,
  subject,
  abs_table,
  frequency,
  region,
  city,
  unit,
  value,
  LAG(value, 1) OVER (PARTITION BY series_key ORDER BY period_start) AS prior_period_value,
  LAG(value, 4) OVER (PARTITION BY series_key ORDER BY period_start) AS value_4_periods_ago,
  CASE
    WHEN LAG(value, 1) OVER (PARTITION BY series_key ORDER BY period_start) IS NULL THEN NULL
    WHEN LAG(value, 1) OVER (PARTITION BY series_key ORDER BY period_start) = 0 THEN NULL
    ELSE value / LAG(value, 1) OVER (PARTITION BY series_key ORDER BY period_start) - 1
  END AS period_change_pct,
  CASE
    WHEN LAG(value, 4) OVER (PARTITION BY series_key ORDER BY period_start) IS NULL THEN NULL
    WHEN LAG(value, 4) OVER (PARTITION BY series_key ORDER BY period_start) = 0 THEN NULL
    ELSE value / LAG(value, 4) OVER (PARTITION BY series_key ORDER BY period_start) - 1
  END AS annual_change_pct
FROM silver.fact_abs_ppi_series;

CREATE OR REPLACE VIEW gold.vw_adelaide_building_market AS
SELECT
  f.date_key,
  d.year,
  d.year_quarter,
  f.series_key,
  f.series_id,
  s.metric,
  s.category_2 AS building_type,
  s.category_3 AS sector_or_work_type,
  s.category_4 AS work_type,
  f.value,
  f.period_change_pct,
  f.annual_change_pct,
  f.unit,
  f.dataset,
  f.abs_table
FROM gold.fact_market_indicators f
JOIN gold.dim_date d ON f.date_key = d.date_key
JOIN gold.dim_series s ON f.series_key = s.series_key
WHERE f.region = 'South Australia'
   OR f.city = 'Adelaide';

OPTIMIZE silver.fact_abs_ppi_series ZORDER BY (series_key, period_start);
OPTIMIZE gold.fact_market_indicators ZORDER BY (series_key, date_key);
