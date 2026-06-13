-- Data quality checks to mention in interview / project walkthrough
USE CATALOG adbri_bi;

-- 1. Row count by source dataset
SELECT
  dataset,
  COUNT(*) AS rows_loaded,
  COUNT(DISTINCT series_key) AS series_count,
  MIN(period_start) AS first_period,
  MAX(period_start) AS latest_period
FROM silver.fact_abs_ppi_series
GROUP BY dataset
ORDER BY dataset;

-- 2. Duplicate grain check: each dataset-series should have only one row per period
SELECT
  series_key,
  period_start,
  COUNT(*) AS duplicate_count
FROM silver.fact_abs_ppi_series
GROUP BY series_key, period_start
HAVING COUNT(*) > 1;

-- 3. Null critical fields
SELECT
  SUM(CASE WHEN series_id IS NULL THEN 1 ELSE 0 END) AS null_series_id,
  SUM(CASE WHEN period_start IS NULL THEN 1 ELSE 0 END) AS null_period_start,
  SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
FROM silver.fact_abs_ppi_series;

-- 4. Latest indicators for Adelaide / South Australia
SELECT
  s.dataset,
  s.series_description,
  f.date_key,
  f.value,
  f.period_change_pct,
  f.annual_change_pct
FROM gold.fact_market_indicators f
JOIN gold.dim_series s ON f.series_key = s.series_key
WHERE f.date_key = (SELECT MAX(date_key) FROM gold.fact_market_indicators)
  AND (s.region = 'South Australia' OR s.city = 'Adelaide')
ORDER BY s.dataset, s.series_description;
