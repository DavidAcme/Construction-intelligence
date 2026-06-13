# Power BI Model and DAX

## Connection

Recommended flow for the portfolio demo:

1. Databricks SQL Warehouse > Connection details.
2. Power BI Desktop > Get Data > Azure Databricks.
3. Use the Databricks server hostname and HTTP path.
4. Import mode for a fast demo, DirectQuery if you want to show near-real-time Databricks serving.
5. Load:
   - `gold.fact_market_indicators`
   - `gold.dim_series`
   - `gold.dim_date`
   - optional view: `gold.vw_adelaide_building_market`

## Relationships

Use a simple star schema:

| From | To | Cardinality | Filter Direction |
|---|---|---:|---|
| `gold.fact_market_indicators[date_key]` | `gold.dim_date[date_key]` | Many-to-one | Single |
| `gold.fact_market_indicators[series_key]` | `gold.dim_series[series_key]` | Many-to-one | Single |

Hide technical fields after relationships are working:

- Hide `fact_market_indicators[series_key]`, `fact_market_indicators[series_id]`, and `fact_market_indicators[date_key]`.
- Keep `dim_series[series_description]`, `dataset`, `subject`, `frequency`, `region`, `city`, categories.
- Sort `dim_date[year_month]` by `dim_date[date_key]`.

## Measures

```DAX
Total Value :=
SUM ( fact_market_indicators[value] )

Latest Date :=
MAX ( fact_market_indicators[date_key] )

Latest Value :=
VAR LatestVisibleDate =
    [Latest Date]
RETURN
    CALCULATE (
        [Total Value],
        fact_market_indicators[date_key] = LatestVisibleDate
    )

Previous Period Value :=
VAR CurrentDate =
    MAX ( fact_market_indicators[date_key] )
VAR PreviousDate =
    MAXX (
        FILTER (
            ALLSELECTED ( dim_date[date_key] ),
            dim_date[date_key] < CurrentDate
        ),
        dim_date[date_key]
    )
RETURN
    CALCULATE (
        [Total Value],
        dim_date[date_key] = PreviousDate
    )

Period Change % :=
VAR PreviousValue = [Previous Period Value]
RETURN
    DIVIDE ( [Total Value] - PreviousValue, PreviousValue )

YoY / 4-Period Change % :=
AVERAGE ( fact_market_indicators[annual_change_pct] )

Building Approvals :=
CALCULATE (
    [Total Value],
    dim_series[subject] = "Building approvals"
)

PPI Index :=
CALCULATE (
    [Total Value],
    CONTAINSSTRING ( dim_series[subject], "Producer price index" )
)

SA / Adelaide Latest :=
CALCULATE (
    [Latest Value],
    FILTER (
        dim_series,
        dim_series[region] = "South Australia"
            || dim_series[city] = "Adelaide"
    )
)

Market Signal :=
VAR Change = [YoY / 4-Period Change %]
RETURN
    SWITCH (
        TRUE (),
        Change >= 0.05, "High inflation / demand pressure",
        Change >= 0.02, "Moderate growth",
        Change <= -0.02, "Softening",
        "Stable"
    )
```

## Report Pages

### Page 1: Executive Market Pulse

Purpose: show Adbri stakeholders whether the SA construction market is expanding, softening, or facing cost pressure.

Visuals:

- KPI cards: latest dwelling approvals, latest Adelaide/SA PPI index, YoY or 4-period change.
- Line chart: building approvals trend by building type or sector.
- Line chart: PPI input/output trend for Adelaide / South Australia.
- Slicer: dataset, frequency, building type, sector, date.
- Small table: latest period by series with value and annual change.

### Page 2: Building Approvals Demand

Purpose: demand-side view for cement, concrete, aggregates, lime, and masonry demand conversations.

Visuals:

- Monthly line chart: total dwelling units approved in South Australia.
- Stacked column: private vs public sector / houses vs other residential.
- Matrix: year by building type, with conditional formatting on YoY change.
- Tooltip: ABS table, series id, unit, source file.

### Page 3: Construction Cost Pressure

Purpose: supply-side view using Producer Price Index data.

Visuals:

- Quarterly line chart: output of construction industries, South Australia.
- Quarterly line chart: input to house construction industry, Adelaide vs weighted average of six capital cities.
- Bar chart: latest annual change by input category or city.
- KPI: cost pressure status using `Market Signal`.

### Page 4: Data Quality and Lineage

Purpose: show BI professionalism, not just chart building.

Visuals:

- Row counts by dataset.
- Distinct series count by dataset.
- First/latest period by dataset.
- Duplicate grain check result.
- Data flow diagram: Excel source > Databricks Bronze > Silver > Gold > Power BI.

## Design Notes

- Keep colours close to Adbri branding: deep blue, cyan, white, neutral grey.
- Use dense operational layout, not a marketing page.
- Use clear titles: "SA Construction Demand", "Construction Cost Pressure", "Latest Market Signal".
- Format numbers:
  - approvals: whole number
  - index values: one decimal
  - percentage change: one decimal percentage
- Use Power BI bookmarks only after the core model and measures are correct.
