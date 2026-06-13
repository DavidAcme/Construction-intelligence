# Data Dictionary

## Source Files

| File | ABS table | Business use |
|---|---|---|
| `Building_Approvals_SA_Table04.xlsx` | 8731.0 Table 04 | SA dwelling approvals by sector and building type, all series |
| `Building_Approvals_SA_Table15.xlsx` | 8731.0 Table 15 | SA original dwelling approvals by sector and work type |
| `PPI_Construction_Output_Table17.xlsx` | 6427.0 Table 17 | Construction output price indexes by state and industry class |
| `PPI_House_Construction_Input_Table18.xlsx` | 6427.0 Table 18 | House construction input price indexes by capital city and group |

## Tidy CSV Columns

| Column | Meaning |
|---|---|
| `source_file` | Original Excel workbook name |
| `dataset` | Stable machine-readable dataset name |
| `series_key` | Power BI-safe key: `dataset + "|" + series_id` |
| `subject` | Business subject, such as building approvals or PPI |
| `abs_table` | ABS publication and table reference |
| `period_start` | Month or quarter start date |
| `year`, `quarter`, `month` | Calendar attributes for modelling |
| `value` | Numeric observation |
| `series_id` | ABS series identifier |
| `series_description` | Original ABS description |
| `unit` | Number or index number |
| `series_type` | Original, seasonally adjusted, trend, or similar |
| `data_type` | FLOW or INDEX |
| `frequency` | Month or Quarter |
| `series_start`, `series_end`, `no_obs` | ABS metadata |
| `metric` | Parsed first part of ABS description |
| `category_1` to `category_5` | Parsed business attributes from ABS description |
| `region` | Parsed state or Australia when present |
| `city` | Parsed capital city when present |

## Grain

The fact table grain is:

`one row per series_key per period_start`

This is the key sentence to use in interviews because it shows you understand the model before building visuals.

## Business Interpretation For Adbri

- Building approvals are a demand proxy for future residential and non-residential construction activity.
- Construction output PPI indicates price movement in construction delivery.
- House construction input PPI indicates material and input cost pressure, including Adelaide compared with other capital cities.
- Together they support a market pulse dashboard for a building materials company: demand, cost pressure, trend direction, and regional focus.
