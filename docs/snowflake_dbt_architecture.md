# Snowflake + dbt architecture and transformation log

## Why this layer exists

The original Tableau project used compact local summaries. This upgrade adds a documented ELT flow so the same operational metrics are produced from a governed fact table, testable dbt models, and reconciliation checks before Tableau receives an aggregate extract.

## Architecture and model flow

```text
CFPB CSV (2023-2025 prepared extract)
  -> RAW.COMPLAINTS_CSV
  -> stg_complaints
  -> int_complaints_enriched
  -> dimensions + fct_complaints
  -> Tableau-ready marts + reconciliation mart
  -> aggregate CSV exports + CFPB_Tableau_Source.xlsx
  -> single Tableau Public dashboard
```

`RAW.COMPLAINTS_CSV` does not contain the source narrative, ZIP code, or tags. The raw table is a landing layer, not a public data product.

## Transformation log

| Step | Transformation | Reason / check |
|---|---|---|
| 1 | Download official CFPB CSV and process in pandas chunks | Handles a source larger than spreadsheet limits without loading all rows into memory |
| 2 | Keep full calendar years 2023–2025 | Enables comparable year-over-year analysis; excludes partial 2026 |
| 3 | Select analysis fields and exclude narrative, ZIP, and tags | Minimizes privacy exposure and avoids unused fields |
| 4 | Normalize blank categorical values to `Unknown` | Prevents missing records from disappearing from counts |
| 5 | Cast Date received and Complaint ID | Establishes the date and one-record-per-Complaint-ID grain |
| 6 | Validate duplicate IDs and date coverage locally | Baseline evidence: 9,363,711 rows, 9,363,711 unique IDs, 0 duplicates |
| 7 | Load prepared extract to Snowflake `RAW.COMPLAINTS_CSV` | Preserves raw-as-loaded fields for reproducible staging |
| 8 | dbt staging models standardize values and mark valid complaints | Makes definitions reusable across every mart |
| 9 | dbt fact/dimensions model the complaint grain and allowed relationships | Separates canonical detail from dashboard aggregates |
| 10 | dbt marts calculate volumes, rates, shares, ranks, rolling and period comparisons | Gives Tableau compact, documented, query-ready data |
| 11 | dbt tests and `validate_snowflake_pipeline.py` reconcile source, fact, and marts | Blocks dashboard refresh if metric totals disagree |
| 12 | Export only compact aggregate marts to Tableau | Tableau Public receives a snapshot, not raw data or a live warehouse connection |

## dbt tests

- `not_null` and `unique` on Complaint ID in the staging and fact layers.
- `not_null` / allowed-value checks on Date received and timely-response labels.
- Relationship tests from the fact table to date, company, and state dimensions.
- Reconciliation mart checks for raw-to-fact row count, raw distinct Complaint IDs, and mart-to-fact totals.

## Cost and access guardrails

- The setup script uses an X-Small warehouse with `AUTO_SUSPEND = 60` and `AUTO_RESUME = TRUE`.
- Credentials are read only from local environment variables. `.env` and the local dbt profile directory are ignored by Git.
- `load_to_snowflake.py` refuses to overwrite a nonempty raw table unless `--replace` is explicitly supplied.
- The local stage can be cleared with `--remove-staged-file` after successful validation.

## Execution evidence

The Snowflake deployment was executed on 2026-07-29 with the restricted `CFPB_PORTFOLIO_ROLE` after one-time setup:

1. `dbt debug` confirmed the account, warehouse, database, role, and profile connection.
2. `dbt run` built 15 models, including a 9,363,711-row fact table.
3. `dbt test` passed all 31 data-quality and relationship tests.
4. `data/processed/snowflake_validation.json` recorded six passing source-to-fact and fact-to-mart checks.
5. `data/exports/tableau/*.csv` and `tableau/CFPB_Tableau_Source.xlsx` were regenerated from the dbt marts.

The remaining public-facing step is to refresh and republish the existing Tableau Public dashboard from this extract snapshot. Tableau Public remains an extract-based presentation layer, not a live Snowflake connection.
