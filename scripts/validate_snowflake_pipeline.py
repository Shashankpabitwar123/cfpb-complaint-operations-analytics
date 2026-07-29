#!/usr/bin/env python3
"""Run source-to-model and model-to-Tableau-mart reconciliation checks in Snowflake."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "snowflake_validation.json"

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


CHECKS = {
    "raw_to_fact_row_count": """
        select
          (select count(*) from raw.complaints_csv) as expected_value,
          (select count(*) from analytics.fct_complaints) as actual_value
    """,
    "raw_distinct_id_to_fact_count": """
        select
          (select count(distinct complaint_id_raw) from raw.complaints_csv) as expected_value,
          (select count(*) from analytics.fct_complaints) as actual_value
    """,
    "monthly_mart_to_fact_count": """
        select
          (select count(*) from analytics.fct_complaints) as expected_value,
          (select sum(complaint_volume) from analytics.mart_monthly_operations) as actual_value
    """,
    "product_mart_to_fact_count": """
        select
          (select count(*) from analytics.fct_complaints) as expected_value,
          (select sum(complaint_volume) from analytics.mart_product_workload) as actual_value
    """,
    "response_mart_to_fact_count": """
        select
          (select count(*) from analytics.fct_complaints) as expected_value,
          (select sum(complaint_volume) from analytics.mart_response_performance) as actual_value
    """,
    "dbt_quality_mart": """
        select
          count_if(status = 'PASS') as expected_value,
          count(*) as actual_value
        from analytics.mart_data_quality_reconciliation
    """,
}


def normalize(value: object) -> int | float | str | None:
    if hasattr(value, "item"):
        return value.item()
    return value


def main() -> None:
    evidence: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "checks": {},
    }

    with snowflake.connector.connect(**connection_parameters()) as connection:
        with connection.cursor() as cursor:
            for name, query in CHECKS.items():
                cursor.execute(query)
                expected_value, actual_value = cursor.fetchone()
                expected_value, actual_value = normalize(expected_value), normalize(actual_value)
                passed = expected_value == actual_value
                evidence["checks"][name] = {
                    "expected_value": expected_value,
                    "actual_value": actual_value,
                    "difference": actual_value - expected_value,
                    "status": "PASS" if passed else "FAIL",
                }
                if not passed:
                    evidence["status"] = "FAIL"

    OUTPUT_PATH.write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")
    print(json.dumps(evidence, indent=2, default=str))
    if evidence["status"] != "PASS":
        raise SystemExit("Snowflake reconciliation failed; inspect the generated evidence file.")


if __name__ == "__main__":
    main()
