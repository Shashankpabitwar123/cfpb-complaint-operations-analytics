#!/usr/bin/env python3
"""Load the privacy-minimized CFPB 2023-2025 prepared extract into Snowflake.

Credentials are read from environment variables only. The default authentication
method is Snowflake external-browser authentication, so no password is stored in
the repository. Use --replace only when intentionally reloading the raw table.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import snowflake.connector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "data" / "processed" / "cfpb_complaints_2023_2025.csv"
SETUP_SQL = PROJECT_ROOT / "sql" / "snowflake" / "01_setup.sql"


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def connection_parameters(bootstrap: bool = False) -> dict[str, str]:
    """Return safe connection parameters for either bootstrap or project execution.

    During first-run bootstrap the project warehouse/database/schema do not exist,
    so they must not be included in the connection request.
    """
    authenticator = os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser")
    parameters = {
        "account": required_environment("SNOWFLAKE_ACCOUNT"),
        "user": required_environment("SNOWFLAKE_USER"),
        "role": os.getenv("SNOWFLAKE_ROLE", "CFPB_PORTFOLIO_ROLE"),
        "authenticator": authenticator,
    }
    if not bootstrap:
        parameters.update({
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "CFPB_PORTFOLIO_WH"),
            "database": os.getenv("SNOWFLAKE_DATABASE", "CFPB_ANALYTICS"),
            "schema": "RAW",
        })
    if authenticator.lower() != "externalbrowser":
        parameters["password"] = required_environment("SNOWFLAKE_PASSWORD")
    return parameters


def execute_sql_file(cursor: snowflake.connector.cursor.SnowflakeCursor, path: Path) -> None:
    """Execute the intentionally simple, semicolon-delimited setup script."""
    sql_without_comments = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("--")
    )
    for statement in sql_without_comments.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)


def quote_local_file(path: Path) -> str:
    """Snowflake PUT expects a file URI with spaces safely escaped."""
    return path.resolve().as_uri().replace("'", "''")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply-setup",
        action="store_true",
        help="Run sql/snowflake/01_setup.sql first (requires account-level permissions).",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate RAW.COMPLAINTS_CSV before copying. Required for a reload.",
    )
    parser.add_argument(
        "--remove-staged-file",
        action="store_true",
        help="Remove the compressed local file from the Snowflake stage after a successful copy.",
    )
    arguments = parser.parse_args()

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Prepared source not found at {SOURCE_FILE}. Run scripts/prepare_data.py first."
        )

    with snowflake.connector.connect(**connection_parameters(bootstrap=arguments.apply_setup)) as connection:
        with connection.cursor() as cursor:
            if arguments.apply_setup:
                execute_sql_file(cursor, SETUP_SQL)

            cursor.execute("USE WAREHOUSE IDENTIFIER(%s)", (os.getenv("SNOWFLAKE_WAREHOUSE", "CFPB_PORTFOLIO_WH"),))
            cursor.execute("USE DATABASE IDENTIFIER(%s)", (os.getenv("SNOWFLAKE_DATABASE", "CFPB_ANALYTICS"),))
            cursor.execute("USE SCHEMA RAW")

            if arguments.replace:
                cursor.execute("TRUNCATE TABLE COMPLAINTS_CSV")
            else:
                cursor.execute("SELECT COUNT(*) FROM COMPLAINTS_CSV")
                existing_rows = cursor.fetchone()[0]
                if existing_rows:
                    raise RuntimeError(
                        "RAW.COMPLAINTS_CSV is not empty. Use --replace only if you intentionally want to reload it."
                    )

            stage_path = "@CFPB_LOCAL_STAGE/cfpb_complaints_2023_2025.csv.gz"
            cursor.execute(
                f"PUT '{quote_local_file(SOURCE_FILE)}' {stage_path} AUTO_COMPRESS=TRUE OVERWRITE=TRUE PARALLEL=4"
            )

            cursor.execute(
                """
                COPY INTO COMPLAINTS_CSV (
                    DATE_RECEIVED_RAW, PRODUCT_RAW, SUB_PRODUCT_RAW, ISSUE_RAW, SUB_ISSUE_RAW,
                    COMPANY_PUBLIC_RESPONSE_RAW, COMPANY_RAW, STATE_RAW, SUBMITTED_VIA_RAW,
                    DATE_SENT_TO_COMPANY_RAW, COMPANY_RESPONSE_TO_CONSUMER_RAW, TIMELY_RESPONSE_RAW,
                    COMPLAINT_ID_RAW, YEAR_RAW, MONTH_START_RAW, HAS_COMPANY_RESPONSE_RAW,
                    TIMELY_RESPONSE_FLAG_RAW
                )
                FROM (
                    SELECT
                        t.$1, t.$2, t.$3, t.$4, t.$5, t.$6, t.$7, t.$8,
                        t.$11, t.$12, t.$13, t.$14, t.$15, t.$16, t.$17, t.$18, t.$19
                    FROM @CFPB_LOCAL_STAGE/cfpb_complaints_2023_2025.csv.gz
                         (FILE_FORMAT => 'CFPB_CSV_FORMAT') t
                )
                ON_ERROR = 'ABORT_STATEMENT'
                """
            )

            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT COMPLAINT_ID_RAW) FROM COMPLAINTS_CSV")
            total_rows, distinct_ids = cursor.fetchone()
            print(f"Loaded {total_rows:,} rows with {distinct_ids:,} distinct raw Complaint IDs.")

            if arguments.remove_staged_file:
                cursor.execute(f"REMOVE {stage_path}")
                print("Removed the staged compressed source file.")


if __name__ == "__main__":
    main()
