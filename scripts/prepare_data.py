#!/usr/bin/env python3
"""Create a privacy-safe, reproducible CFPB complaint analysis dataset."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/complaints.csv"
PROCESSED_PATH = ROOT / "data/processed/cfpb_complaints_2023_2025.csv"
PROFILE_PATH = ROOT / "data/processed/data_profile.json"
EXCEL_PATH = ROOT / "excel/CFPB_data_quality_review.xlsx"

START_DATE = pd.Timestamp("2023-01-01", tz="UTC")
END_DATE = pd.Timestamp("2026-01-01", tz="UTC")
CHUNK_SIZE = 200_000

KEEP_COLUMNS = [
    "Date received",
    "Product",
    "Sub-product",
    "Issue",
    "Sub-issue",
    "Company public response",
    "Company",
    "State",
    "ZIP code",
    "Tags",
    "Submitted via",
    "Date sent to company",
    "Company response to consumer",
    "Timely response?",
    "Complaint ID",
]

CATEGORY_COLUMNS = [
    "Product",
    "Sub-product",
    "Issue",
    "Sub-issue",
    "Company public response",
    "Company",
    "State",
    "Tags",
    "Submitted via",
    "Company response to consumer",
    "Timely response?",
]


def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Normalize types and filter to the complete analysis window."""
    chunk["Date received"] = pd.to_datetime(chunk["Date received"], errors="coerce", utc=True)
    chunk["Date sent to company"] = pd.to_datetime(
        chunk["Date sent to company"], errors="coerce", utc=True
    )
    chunk = chunk.loc[
        (chunk["Date received"] >= START_DATE)
        & (chunk["Date received"] < END_DATE)
    ].copy()

    for column in CATEGORY_COLUMNS:
        chunk[column] = chunk[column].astype("string").str.strip()
        chunk[column] = chunk[column].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        chunk[column] = chunk[column].fillna("Unknown")

    chunk["ZIP code"] = chunk["ZIP code"].astype("string").str.strip().fillna("Unknown")
    chunk["Complaint ID"] = chunk["Complaint ID"].astype("string").str.strip()
    chunk["year"] = chunk["Date received"].dt.year.astype("Int64")
    chunk["month_start"] = (
        chunk["Date received"].dt.tz_localize(None).dt.to_period("M").astype("string")
    )
    chunk["has_company_response"] = (
        chunk["Company response to consumer"].ne("Unknown").astype("int8")
    )
    chunk["timely_response_flag"] = chunk["Timely response?"].where(
        chunk["Timely response?"].isin(["Yes", "No"]), "Unknown"
    )

    # Keep dates as ISO dates in the portable CSV used by SQL/Tableau.
    chunk["Date received"] = chunk["Date received"].dt.strftime("%Y-%m-%d")
    chunk["Date sent to company"] = chunk["Date sent to company"].dt.strftime("%Y-%m-%d")
    return chunk


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Missing raw CFPB file: {RAW_PATH}")

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PROCESSED_PATH.exists():
        PROCESSED_PATH.unlink()

    row_count = 0
    raw_row_count = 0
    duplicate_id_count = 0
    id_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    category_counts: dict[str, Counter[str]] = {
        column: Counter() for column in CATEGORY_COLUMNS
    }
    selected_year_counts: Counter[str] = Counter()
    raw_min_date = None
    raw_max_date = None
    wrote_header = False

    for chunk in pd.read_csv(
        RAW_PATH,
        usecols=KEEP_COLUMNS,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        raw_row_count += len(chunk)
        raw_dates = pd.to_datetime(chunk["Date received"], errors="coerce", utc=True)
        chunk_min = raw_dates.min()
        chunk_max = raw_dates.max()
        if pd.notna(chunk_min) and (raw_min_date is None or chunk_min < raw_min_date):
            raw_min_date = chunk_min
        if pd.notna(chunk_max) and (raw_max_date is None or chunk_max > raw_max_date):
            raw_max_date = chunk_max

        cleaned = clean_chunk(chunk)
        if cleaned.empty:
            continue

        row_count += len(cleaned)
        duplicate_id_count += int(cleaned["Complaint ID"].duplicated().sum())
        id_counts.update(cleaned["Complaint ID"].tolist())
        selected_year_counts.update(cleaned["year"].astype(str).tolist())

        for column in KEEP_COLUMNS:
            missing_counts[column] += int(chunk[column].isna().sum())
        for column in CATEGORY_COLUMNS:
            category_counts[column].update(cleaned[column].value_counts().to_dict())

        cleaned.to_csv(
            PROCESSED_PATH,
            mode="a",
            index=False,
            header=not wrote_header,
        )
        wrote_header = True

    duplicate_ids = sum(1 for count in id_counts.values() if count > 1)
    profile = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(RAW_PATH.relative_to(ROOT)),
        "processed_file": str(PROCESSED_PATH.relative_to(ROOT)),
        "analysis_window": {
            "start": "2023-01-01",
            "end_exclusive": "2026-01-01",
            "years": [2023, 2024, 2025],
            "reason": "2026 is partial in the downloaded source; the raw maximum Date received is 2026-07-26.",
        },
        "raw_row_count": raw_row_count,
        "raw_date_min": raw_min_date.strftime("%Y-%m-%d") if raw_min_date is not None else None,
        "raw_date_max": raw_max_date.strftime("%Y-%m-%d") if raw_max_date is not None else None,
        "processed_row_count": row_count,
        "processed_unique_complaint_ids": len(id_counts),
        "duplicate_rows_in_processed_window": duplicate_id_count,
        "duplicate_complaint_ids_in_processed_window": duplicate_ids,
        "processed_year_counts": dict(sorted(selected_year_counts.items())),
        "raw_missing_counts": dict(missing_counts),
        "category_cardinality": {
            column: len(counts) for column, counts in category_counts.items()
        },
        "privacy_decision": "Consumer complaint narrative was excluded from the processed dataset and public artifacts.",
    }
    PROFILE_PATH.write_text(json.dumps(profile, indent=2) + "\n")

    kpi_definitions = pd.DataFrame(
        [
            ["Complaint volume", "COUNT(DISTINCT Complaint ID)", "Distinct complaints in the selected complete-year window."],
            ["Monthly complaint volume", "COUNT(DISTINCT Complaint ID) by month_start", "Trend measure; do not compare partial periods without labeling them."],
            ["Response coverage", "Complaints with known Company response to consumer / total complaints", "Shows how many published complaints have a known response outcome."],
            ["Timely response rate", "Timely response = Yes / known Yes or No timely-response values", "Denominator excludes unknown timely-response values."],
            ["Closed-with-explanation share", "Closed with explanation / known response outcomes", "A response-outcome mix measure, not a quality ranking."],
            ["Channel mix", "COUNT(DISTINCT Complaint ID) by Submitted via", "Describes how complaints entered the CFPB system."],
        ],
        columns=["KPI", "Formula", "Interpretation"],
    )
    qa_summary = pd.DataFrame(
        [
            ["Raw row count", raw_row_count],
            ["Raw date minimum", profile["raw_date_min"]],
            ["Raw date maximum", profile["raw_date_max"]],
            ["Processed row count", row_count],
            ["Processed unique Complaint IDs", len(id_counts)],
            ["Duplicate rows in processed window", duplicate_id_count],
            ["Duplicate Complaint IDs in processed window", duplicate_ids],
            ["Analysis start", "2023-01-01"],
            ["Analysis end", "2025-12-31"],
            ["Narrative included", "No"],
        ],
        columns=["Check", "Value"],
    )
    missingness = pd.DataFrame(
        [[column, count] for column, count in missing_counts.items()],
        columns=["Column", "Raw missing values"],
    ).sort_values("Raw missing values", ascending=False)
    category_rows = [
        [column, category, count]
        for column, counts in category_counts.items()
        for category, count in counts.most_common(50)
    ]
    category_table = pd.DataFrame(
        category_rows,
        columns=["Column", "Category", "Processed row count"],
    )
    with pd.ExcelWriter(EXCEL_PATH, engine="xlsxwriter") as writer:
        qa_summary.to_excel(writer, sheet_name="QA Summary", index=False)
        missingness.to_excel(writer, sheet_name="Missingness", index=False)
        category_table.to_excel(writer, sheet_name="Category Counts", index=False)
        kpi_definitions.to_excel(writer, sheet_name="KPI Definitions", index=False)

    print(json.dumps(profile, indent=2))
    print(f"Wrote {PROCESSED_PATH}")
    print(f"Wrote {EXCEL_PATH}")


if __name__ == "__main__":
    main()
