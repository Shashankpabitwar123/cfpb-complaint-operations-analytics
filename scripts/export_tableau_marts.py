#!/usr/bin/env python3
"""Export compact Tableau Public-safe snapshots from Snowflake dbt marts.

Tableau Public supports extracts, not a live Snowflake connection. This script
creates only aggregate mart CSVs for the single published dashboard.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import snowflake.connector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "exports" / "tableau"
MARTS = {
    "mart_monthly_operations": "MART_MONTHLY_OPERATIONS",
    "mart_product_workload": "MART_PRODUCT_WORKLOAD",
    "mart_issue_workload": "MART_ISSUE_WORKLOAD",
    "mart_response_performance": "MART_RESPONSE_PERFORMANCE",
    "mart_channel_mix": "MART_CHANNEL_MIX",
    "mart_state_workload": "MART_STATE_WORKLOAD",
    "mart_company_concentration": "MART_COMPANY_CONCENTRATION",
    "mart_data_quality_reconciliation": "MART_DATA_QUALITY_RECONCILIATION",
}


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def connection_parameters() -> dict[str, str]:
    authenticator = os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser")
    parameters = {
        "account": required_environment("SNOWFLAKE_ACCOUNT"),
        "user": required_environment("SNOWFLAKE_USER"),
        "role": os.getenv("SNOWFLAKE_ROLE", "CFPB_PORTFOLIO_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "CFPB_PORTFOLIO_WH"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "CFPB_ANALYTICS"),
        "schema": "ANALYTICS",
        "authenticator": authenticator,
    }
    if authenticator.lower() != "externalbrowser":
        parameters["password"] = required_environment("SNOWFLAKE_PASSWORD")
    return parameters


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with snowflake.connector.connect(**connection_parameters()) as connection:
        with connection.cursor() as cursor:
            for filename, relation in MARTS.items():
                cursor.execute(f"SELECT * FROM {relation}")
                path = OUTPUT_DIR / f"{filename}.csv"
                with path.open("w", newline="", encoding="utf-8") as output_file:
                    writer = csv.writer(output_file)
                    writer.writerow([column[0].lower() for column in cursor.description])
                    writer.writerows(cursor.fetchall())
                print(f"Exported {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
