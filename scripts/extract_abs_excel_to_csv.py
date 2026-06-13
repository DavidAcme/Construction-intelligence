from __future__ import annotations

import csv
import os
import re
import argparse
from datetime import datetime
from pathlib import Path

import openpyxl


DEFAULT_SOURCE_DIR = Path(
    os.environ.get("ADBRI_SOURCE_DIR", Path(__file__).resolve().parents[1] / "source_data")
)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"

SOURCES = [
    {
        "file": "Building_Approvals_SA_Table04.xlsx",
        "dataset": "building_approvals_sa_table04",
        "subject": "Building approvals",
        "abs_table": "8731.0 Table 04",
    },
    {
        "file": "Building_Approvals_SA_Table15.xlsx",
        "dataset": "building_approvals_sa_table15",
        "subject": "Building approvals",
        "abs_table": "8731.0 Table 15",
    },
    {
        "file": "PPI_Construction_Output_Table17.xlsx",
        "dataset": "ppi_construction_output_table17",
        "subject": "Producer price index - construction output",
        "abs_table": "6427.0 Table 17",
    },
    {
        "file": "PPI_House_Construction_Input_Table18.xlsx",
        "dataset": "ppi_house_construction_input_table18",
        "subject": "Producer price index - house construction input",
        "abs_table": "6427.0 Table 18",
    },
]


def clean_part(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def split_description(description: str) -> dict[str, str]:
    parts = [clean_part(p) for p in description.split(";") if clean_part(p)]
    parsed: dict[str, str] = {
        "metric": parts[0] if parts else "",
        "category_1": parts[1] if len(parts) > 1 else "",
        "category_2": parts[2] if len(parts) > 2 else "",
        "category_3": parts[3] if len(parts) > 3 else "",
        "category_4": parts[4] if len(parts) > 4 else "",
        "category_5": parts[5] if len(parts) > 5 else "",
    }

    text = " | ".join(parts)
    for state in [
        "South Australia",
        "New South Wales",
        "Victoria",
        "Queensland",
        "Western Australia",
        "Tasmania",
        "Northern Territory",
        "Australian Capital Territory",
        "Australia",
    ]:
        if state in text:
            parsed["region"] = state
            break
    else:
        parsed["region"] = ""

    for city in [
        "Adelaide",
        "Sydney",
        "Melbourne",
        "Brisbane",
        "Perth",
        "Hobart",
        "Darwin",
        "Canberra",
        "Weighted Average of 6 Capital Cities",
    ]:
        if city in text:
            parsed["city"] = city
            break
    else:
        parsed["city"] = ""

    return parsed


def iso_date(value: object) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value) if value is not None else ""


def extract_source(
    source: dict[str, str],
    source_dir: Path,
) -> list[dict[str, object]]:
    path = source_dir / source["file"]
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Data1"]
    data = list(ws.iter_rows(values_only=True))

    headers = {}
    for col_index, description in enumerate(data[0][1:], start=1):
        if not description:
            continue
        parsed = split_description(str(description))
        headers[col_index] = {
            "series_description": clean_part(str(description)),
            "unit": data[1][col_index],
            "series_type": data[2][col_index],
            "data_type": data[3][col_index],
            "frequency": data[4][col_index],
            "collection_month": data[5][col_index],
            "series_start": iso_date(data[6][col_index]),
            "series_end": iso_date(data[7][col_index]),
            "no_obs": data[8][col_index],
            "series_id": data[9][col_index],
            **parsed,
        }

    rows: list[dict[str, object]] = []
    for source_row in data[10:]:
        period = source_row[0]
        if period is None:
            continue
        for col_index, meta in headers.items():
            value = source_row[col_index]
            if value is None:
                continue
            rows.append(
                {
                    "source_file": source["file"],
                    "dataset": source["dataset"],
                    "series_key": f"{source['dataset']}|{meta['series_id']}",
                    "subject": source["subject"],
                    "abs_table": source["abs_table"],
                    "period_start": iso_date(period),
                    "year": period.year if isinstance(period, datetime) else "",
                    "quarter": ((period.month - 1) // 3 + 1) if isinstance(period, datetime) else "",
                    "month": period.month if isinstance(period, datetime) else "",
                    "value": value,
                    **meta,
                }
            )

    wb.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert the four ABS Excel workbooks to tidy CSV files."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing the four source XLSX files.",
    )
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    fieldnames: list[str] | None = None

    for source in SOURCES:
        rows = extract_source(source, source_dir)
        all_rows.extend(rows)
        fieldnames = list(rows[0].keys()) if rows and fieldnames is None else fieldnames
        out_path = OUTPUT_DIR / f"{source['dataset']}.csv"
        with out_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"{out_path.name}: {len(rows):,} rows")

    if not fieldnames:
        raise RuntimeError("No rows extracted from source workbooks.")

    combined_path = OUTPUT_DIR / "adbri_abs_ppi_combined_long.csv"
    with combined_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"{combined_path.name}: {len(all_rows):,} rows")


if __name__ == "__main__":
    main()
