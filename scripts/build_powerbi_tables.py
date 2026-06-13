from __future__ import annotations

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT = BASE_DIR / "outputs" / "adbri_abs_ppi_combined_long.csv"
POWERBI_DIR = BASE_DIR / "powerbi" / "data"


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read_rows()

    date_seen = {}
    for row in rows:
        date_seen[row["period_start"]] = {
            "date_key": row["period_start"],
            "year": row["year"],
            "quarter": row["quarter"],
            "month": row["month"],
            "year_month": row["period_start"][:7],
            "year_quarter": f"{row['year']}-Q{row['quarter']}",
        }

    series_seen = {}
    for row in rows:
        key = row["series_key"]
        series_seen[key] = {
            "series_key": key,
            "series_id": row["series_id"],
            "dataset": row["dataset"],
            "subject": row["subject"],
            "abs_table": row["abs_table"],
            "series_description": row["series_description"],
            "unit": row["unit"],
            "series_type": row["series_type"],
            "data_type": row["data_type"],
            "frequency": row["frequency"],
            "metric": row["metric"],
            "category_1": row["category_1"],
            "category_2": row["category_2"],
            "category_3": row["category_3"],
            "category_4": row["category_4"],
            "category_5": row["category_5"],
            "region": row["region"],
            "city": row["city"],
        }

    fact_rows = []
    previous_by_series: dict[str, list[tuple[str, float]]] = {}
    for row in sorted(rows, key=lambda r: (r["series_key"], r["period_start"])):
        series_rows = previous_by_series.setdefault(row["series_key"], [])
        value = float(row["value"])
        previous_value = series_rows[-1][1] if series_rows else None
        value_4_periods_ago = series_rows[-4][1] if len(series_rows) >= 4 else None
        period_change = None if previous_value in (None, 0) else value / previous_value - 1
        annual_change = None if value_4_periods_ago in (None, 0) else value / value_4_periods_ago - 1
        fact_rows.append(
            {
                "date_key": row["period_start"],
                "series_key": row["series_key"],
                "dataset": row["dataset"],
                "subject": row["subject"],
                "frequency": row["frequency"],
                "region": row["region"],
                "city": row["city"],
                "unit": row["unit"],
                "value": value,
                "prior_period_value": previous_value,
                "value_4_periods_ago": value_4_periods_ago,
                "period_change_pct": period_change,
                "annual_change_pct": annual_change,
            }
        )
        series_rows.append((row["period_start"], value))

    write_csv(
        POWERBI_DIR / "dim_date.csv",
        sorted(date_seen.values(), key=lambda r: r["date_key"]),
        ["date_key", "year", "quarter", "month", "year_month", "year_quarter"],
    )
    write_csv(
        POWERBI_DIR / "dim_series.csv",
        sorted(series_seen.values(), key=lambda r: r["series_key"]),
        [
            "series_key",
            "series_id",
            "dataset",
            "subject",
            "abs_table",
            "series_description",
            "unit",
            "series_type",
            "data_type",
            "frequency",
            "metric",
            "category_1",
            "category_2",
            "category_3",
            "category_4",
            "category_5",
            "region",
            "city",
        ],
    )
    write_csv(
        POWERBI_DIR / "fact_market_indicators.csv",
        fact_rows,
        [
            "date_key",
            "series_key",
            "dataset",
            "subject",
            "frequency",
            "region",
            "city",
            "unit",
            "value",
            "prior_period_value",
            "value_4_periods_ago",
            "period_change_pct",
            "annual_change_pct",
        ],
    )
    print(f"dim_date: {len(date_seen):,}")
    print(f"dim_series: {len(series_seen):,}")
    print(f"fact_market_indicators: {len(fact_rows):,}")


if __name__ == "__main__":
    main()
