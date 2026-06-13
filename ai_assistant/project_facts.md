# Adbri Project Authoritative Facts

## Why series_key was created

`series_id` is not guaranteed to be unique across all four ABS source
workbooks. The same ABS series can appear in more than one table. Therefore,
the project creates a composite key:

`series_key = dataset + "|" + series_id`

This prevents duplicate keys in `dim_series` and creates reliable Power BI and
Databricks relationships.

## Fact table grain

The analytical fact table grain is:

`one row per series_key per period_start`

## Medallion layers

- Bronze stores the raw combined CSV with minimal transformation.
- Silver applies data types, removes invalid critical rows, and preserves
  business metadata.
- Gold publishes `fact_market_indicators`, `dim_date`, and `dim_series` for
  Power BI.

## Market findings

- South Australia building approvals recovered in 2025 compared with the
  weaker 2022-2023 period.
- Selected annual approvals increased from approximately 24,474 in 2024 to
  29,623 in 2025.
- March 2026 selected approvals were approximately 8.6% above March 2025.
- Adelaide house construction input PPI increased approximately 3.7% from
  March 2025 to March 2026.
- South Australia building construction output PPI increased approximately
  3.8% over the same period.
