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
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "exports" / "tableau"
MARTS = {
    "mart_monthly_operations": ("MART_MONTHLY_OPERATIONS", "MONTH_START"),
    "mart_product_workload": ("MART_PRODUCT_WORKLOAD", "RECEIVED_YEAR, PRODUCT"),
    "mart_issue_workload": ("MART_ISSUE_WORKLOAD", "RECEIVED_YEAR, PRODUCT, ISSUE_VOLUME_RANK_WITHIN_PRODUCT"),
    "mart_response_performance": ("MART_RESPONSE_PERFORMANCE", "RECEIVED_YEAR, PRODUCT, COMPANY_RESPONSE_TO_CONSUMER"),
    "mart_channel_mix": ("MART_CHANNEL_MIX", "RECEIVED_YEAR, CHANNEL_VOLUME_RANK_IN_YEAR"),
    "mart_state_workload": ("MART_STATE_WORKLOAD", "RECEIVED_YEAR, STATE_VOLUME_RANK_IN_YEAR"),
    "mart_company_concentration": ("MART_COMPANY_CONCENTRATION", "RECEIVED_YEAR, COMPANY_VOLUME_RANK_IN_YEAR"),
    "mart_data_quality_reconciliation": ("MART_DATA_QUALITY_RECONCILIATION", "CHECK_NAME"),
}

load_dotenv(PROJECT_ROOT / ".env")


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def connection_parameters() -> dict[str, str]:
    authenticator = os.getenv("SNOWFLAKE_AUTHENTICATOR", "snowflake").lower()
    parameters = {
        "account": required_environment("SNOWFLAKE_ACCOUNT"),
        "user": required_environment("SNOWFLAKE_USER"),
        "role": os.getenv("SNOWFLAKE_ROLE", "CFPB_PORTFOLIO_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "CFPB_PORTFOLIO_WH"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "CFPB_ANALYTICS"),
        "schema": "ANALYTICS",
    }
    if authenticator == "externalbrowser":
        parameters["authenticator"] = "externalbrowser"
    elif authenticator in {"snowflake", "password"}:
        parameters["password"] = required_environment("SNOWFLAKE_PASSWORD")
    else:
        raise RuntimeError("Unsupported SNOWFLAKE_AUTHENTICATOR.")
    return parameters


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with snowflake.connector.connect(**connection_parameters()) as connection:
        with connection.cursor() as cursor:
            for filename, (relation, order_by) in MARTS.items():
                cursor.execute(f"SELECT * FROM {relation} ORDER BY {order_by}")
                path = OUTPUT_DIR / f"{filename}.csv"
                with path.open("w", newline="", encoding="utf-8") as output_file:
                    writer = csv.writer(output_file)
                    writer.writerow([column[0].lower() for column in cursor.description])
                    writer.writerows(cursor.fetchall())
                print(f"Exported {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
