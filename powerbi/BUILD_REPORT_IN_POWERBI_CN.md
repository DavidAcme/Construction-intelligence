# 在 Power BI Desktop 里做 Adbri 报表

## 第 1 步：导入三张 CSV

Power BI Desktop:

1. Home > Get data > Text/CSV
2. 依次导入：
   - `powerbi/data/fact_market_indicators.csv`
   - `powerbi/data/dim_date.csv`
   - `powerbi/data/dim_series.csv`
3. 点击 Load。

## 第 2 步：检查数据类型

在 Power Query 或 Model view 里确认：

| 表 | 字段 | 类型 |
|---|---|---|
| `fact_market_indicators` | `date_key` | Date |
| `fact_market_indicators` | `value` | Decimal Number |
| `fact_market_indicators` | `period_change_pct` | Percentage / Decimal Number |
| `fact_market_indicators` | `annual_change_pct` | Percentage / Decimal Number |
| `dim_date` | `date_key` | Date |
| `dim_date` | `year` | Whole Number |
| `dim_date` | `quarter` | Whole Number |
| `dim_date` | `month` | Whole Number |

## 第 3 步：建关系

Model view 里拖拽建立：

| From | To | Cardinality |
|---|---|---|
| `fact_market_indicators[date_key]` | `dim_date[date_key]` | Many to one |
| `fact_market_indicators[series_key]` | `dim_series[series_key]` | Many to one |

两个关系都用 Single filter direction。

## 第 4 步：新建 Measures

在 `fact_market_indicators` 表上右键 > New measure，粘贴：

```DAX
Total Value =
SUM ( fact_market_indicators[value] )
```

```DAX
Latest Date =
MAX ( fact_market_indicators[date_key] )
```

```DAX
Latest Value =
VAR LatestVisibleDate = [Latest Date]
RETURN
    CALCULATE (
        [Total Value],
        fact_market_indicators[date_key] = LatestVisibleDate
    )
```

```DAX
Average Annual Change % =
AVERAGE ( fact_market_indicators[annual_change_pct] )
```

```DAX
Average Period Change % =
AVERAGE ( fact_market_indicators[period_change_pct] )
```

```DAX
Building Approvals =
CALCULATE (
    [Total Value],
    dim_series[subject] = "Building approvals"
)
```

```DAX
PPI Index =
CALCULATE (
    [Total Value],
    CONTAINSSTRING ( dim_series[subject], "Producer price index" )
)
```

```DAX
Market Signal =
VAR Change = [Average Annual Change %]
RETURN
    SWITCH (
        TRUE (),
        Change >= 0.05, "High inflation / demand pressure",
        Change >= 0.02, "Moderate growth",
        Change <= -0.02, "Softening",
        "Stable"
    )
```

## 第 5 步：第一页 Executive Market Pulse

页面标题：`Adbri SA Construction Market Pulse`

加这些 visual：

1. Card: `[Latest Value]`
2. Card: `[Average Annual Change %]`
3. Card: `[Market Signal]`
4. Line chart:
   - X-axis: `dim_date[date_key]`
   - Y-axis: `[Total Value]`
   - Legend: `dim_series[subject]`
5. Slicer:
   - `dim_series[dataset]`
   - `dim_series[frequency]`
   - `dim_series[category_2]`

## 第 6 步：第二页 Building Approvals Demand

页面标题：`South Australia Building Approvals Demand`

先在 filter pane 过滤：

`dim_series[subject] = Building approvals`

Visuals：

1. Line chart:
   - X-axis: `dim_date[date_key]`
   - Y-axis: `[Building Approvals]`
   - Legend: `dim_series[category_2]`
2. Stacked column chart:
   - X-axis: `dim_date[year]`
   - Y-axis: `[Building Approvals]`
   - Legend: `dim_series[category_3]`
3. Matrix:
   - Rows: `dim_series[category_2]`
   - Columns: `dim_date[year]`
   - Values: `[Building Approvals]`

## 第 7 步：第三页 Construction Cost Pressure

页面标题：`Adelaide Construction Cost Pressure`

Filter:

`dim_series[subject] contains Producer price index`

Visuals：

1. Line chart:
   - X-axis: `dim_date[date_key]`
   - Y-axis: `[PPI Index]`
   - Legend: `dim_series[city]`
2. Bar chart:
   - Y-axis: `dim_series[series_description]`
   - X-axis: `[Average Annual Change %]`
3. Card:
   - `[Market Signal]`

## 第 8 步：第四页 Data Quality

页面标题：`Data Quality and Lineage`

Visuals：

1. Card: Count of `fact_market_indicators[series_key]`
2. Card: Count rows of `fact_market_indicators`
3. Table:
   - `dim_series[dataset]`
   - `dim_series[subject]`
   - count of `dim_series[series_key]`
4. Table:
   - `dim_date[year]`
   - count rows of `fact_market_indicators`

## 面试讲法

> I built a Power BI report using a star schema from Databricks-ready Gold tables. The fact table is at one row per series per period, with separate Date and Series dimensions. The dashboard shows South Australia construction demand using building approvals and Adelaide cost pressure using construction PPI indexes.
