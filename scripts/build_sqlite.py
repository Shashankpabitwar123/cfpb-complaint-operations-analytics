import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/processed/cfpb_complaints_2023_2025.csv"
DB_PATH = ROOT / "data/processed/cfpb_complaints.db"
SUMMARY_DIR = ROOT / "data/processed/summary"

TABLE_COLUMNS = [
    "date_received", "product", "sub_product", "issue", "sub_issue",
    "company_public_response", "company", "state", "zip_code", "tags",
    "submitted_via", "date_sent_to_company", "company_response_to_consumer",
    "timely_response", "complaint_id", "year", "month_start",
    "has_company_response", "timely_response_flag",
]

CREATE_TABLE = """
CREATE TABLE complaints (
    date_received TEXT NOT NULL,
    product TEXT NOT NULL,
    sub_product TEXT NOT NULL,
    issue TEXT NOT NULL,
    sub_issue TEXT NOT NULL,
    company_public_response TEXT NOT NULL,
    company TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    tags TEXT NOT NULL,
    submitted_via TEXT NOT NULL,
    date_sent_to_company TEXT,
    company_response_to_consumer TEXT NOT NULL,
    timely_response TEXT NOT NULL,
    complaint_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    month_start TEXT NOT NULL,
    has_company_response INTEGER NOT NULL,
    timely_response_flag TEXT
)
"""

SUMMARY_QUERIES = {
    "monthly_volume": """
        SELECT month_start, year, COUNT(DISTINCT complaint_id) AS complaint_count
        FROM complaints GROUP BY month_start, year ORDER BY month_start
    """,
    "product_summary": """
        SELECT product, COUNT(DISTINCT complaint_id) AS complaint_count,
               ROUND(100.0 * COUNT(DISTINCT complaint_id) / (SELECT COUNT(DISTINCT complaint_id) FROM complaints), 2) AS share_pct
        FROM complaints GROUP BY product ORDER BY complaint_count DESC
    """,
    "issue_summary": """
        SELECT product, issue, COUNT(DISTINCT complaint_id) AS complaint_count
        FROM complaints GROUP BY product, issue ORDER BY complaint_count DESC
    """,
    "response_performance": """
        SELECT year,
               COUNT(DISTINCT complaint_id) AS complaint_count,
               SUM(has_company_response) AS known_public_response_count,
               ROUND(100.0 * SUM(has_company_response) / COUNT(DISTINCT complaint_id), 2) AS response_coverage_pct,
               SUM(CASE WHEN timely_response_flag = 'Yes' THEN 1 ELSE 0 END) AS timely_yes_count,
               SUM(CASE WHEN timely_response_flag IN ('Yes','No') THEN 1 ELSE 0 END) AS timely_known_count,
               ROUND(100.0 * SUM(CASE WHEN timely_response_flag = 'Yes' THEN 1 ELSE 0 END) /
                     NULLIF(SUM(CASE WHEN timely_response_flag IN ('Yes','No') THEN 1 ELSE 0 END), 0), 2) AS timely_response_rate_pct
        FROM complaints GROUP BY year ORDER BY year
    """,
    "channel_mix": """
        SELECT year, submitted_via, COUNT(DISTINCT complaint_id) AS complaint_count
        FROM complaints GROUP BY year, submitted_via ORDER BY year, complaint_count DESC
    """,
    "state_summary": """
        -- The validated extract has one row per Complaint ID, so COUNT(*) is
        -- equivalent to COUNT(DISTINCT complaint_id) and is much faster here.
        SELECT state, COUNT(*) AS complaint_count
        FROM complaints GROUP BY state ORDER BY complaint_count DESC
    """,
}


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA synchronous = NORMAL")
    con.execute(CREATE_TABLE)
    placeholders = ",".join("?" for _ in TABLE_COLUMNS)
    insert_sql = f"INSERT INTO complaints ({','.join(TABLE_COLUMNS)}) VALUES ({placeholders})"
    with CSV_PATH.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        batch = []
        for row in reader:
            batch.append(tuple(row[col] if row[col] != "" else None for col in [
                "Date received", "Product", "Sub-product", "Issue", "Sub-issue",
                "Company public response", "Company", "State", "ZIP code", "Tags",
                "Submitted via", "Date sent to company", "Company response to consumer",
                "Timely response?", "Complaint ID", "year", "month_start",
                "has_company_response", "timely_response_flag",
            ]))
            if len(batch) >= 50000:
                con.executemany(insert_sql, batch)
                con.commit()
                batch.clear()
        if batch:
            con.executemany(insert_sql, batch)
            con.commit()
    for column in ["complaint_id", "date_received", "product", "issue", "state", "submitted_via"]:
        con.execute(f"CREATE INDEX idx_complaints_{column} ON complaints ({column})")
    con.commit()
    for name, query in SUMMARY_QUERIES.items():
        cur = con.execute(query)
        headers = [d[0] for d in cur.description]
        with (SUMMARY_DIR / f"{name}.csv").open("w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out, lineterminator="\n")
            writer.writerow(headers)
            writer.writerows(cur)
    con.close()
    print(f"Wrote {DB_PATH}")
    print(f"Wrote summaries to {SUMMARY_DIR}")


if __name__ == "__main__":
    main()
