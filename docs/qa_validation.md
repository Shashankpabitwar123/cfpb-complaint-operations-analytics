# Data-quality and reconciliation record

## Rules applied to the local prepared extract

| Rule | Treatment | Baseline result |
|---|---|---:|
| Analysis window | Keep full years 2023–2025; exclude partial 2026 | Pass |
| Record grain | One published record per Complaint ID | Pass |
| Duplicate Complaint IDs | Investigate and stop if count is nonzero | 0 |
| Date received | Must cast to a valid date in the analysis window | Pass |
| Required categories | Preserve blanks as `Unknown`; do not drop source rows | Pass |
| Timely response | Standardize to `Yes`, `No`, or `Unknown` | Pass |
| Privacy fields | Do not include consumer narrative; Snowflake/Tableau additionally omit ZIP and tags | Pass |
| Product taxonomy | Keep source product labels distinct unless a mapping is documented | Pass |

## Completed local reconciliation

| Check | Expected | Actual | Status |
|---|---:|---:|---|
| Processed rows | 9,363,711 | 9,363,711 | Pass |
| Unique Complaint IDs | 9,363,711 | 9,363,711 | Pass |
| Duplicate Complaint IDs | 0 | 0 | Pass |
| Analysis date range | 2023-01-01 to 2025-12-31 | 2023-01-01 to 2025-12-31 | Pass |
| Monthly periods | 36 | 36 | Pass |
| Monthly-summary total | 9,363,711 | 9,363,711 | Pass |
| State-summary total | 9,363,711 | 9,363,711 | Pass |
| Consumer narrative in processed extract | No | No | Pass |

## Completed Snowflake/dbt checks

These checks were executed on 2026-07-29 after loading the privacy-minimized 2023–2025 extract. They are implemented in `mart_data_quality_reconciliation` and `scripts/validate_snowflake_pipeline.py`, and must be rerun after every raw reload and before publishing a Tableau extract.

| Check | Comparison | Executed result |
|---|---|---|
| Raw-to-fact row count | `raw.complaints_csv` vs `fct_complaints` | 9,363,711 = 9,363,711 — Pass |
| Raw distinct IDs-to-fact count | Raw distinct Complaint IDs vs fact rows | 9,363,711 = 9,363,711 — Pass |
| Fact duplicate IDs | Fact rows vs distinct Complaint IDs | 0 — Pass |
| Invalid dates in fact | Null Date received values | 0 — Pass |
| Monthly mart reconciliation | Sum of `mart_monthly_operations.complaint_volume` vs fact rows | 9,363,711 = 9,363,711 — Pass |
| Product mart reconciliation | Sum of `mart_product_workload.complaint_volume` vs fact rows | 9,363,711 = 9,363,711 — Pass |
| Response mart reconciliation | Sum of `mart_response_performance.complaint_volume` vs fact rows | 9,363,711 = 9,363,711 — Pass |
| dbt schema tests | `dbt test` | 31 passed, 0 warnings, 0 errors |

## Tableau reconciliation protocol

After rebuilding the aggregate workbook and refreshing Tableau:

1. Filter the dashboard to All years and compare Total Complaints with `fct_complaints` and `mart_monthly_operations` total.
2. Compare annual volume cards with `mart_monthly_operations` grouped by `received_year`.
3. Compare Product Workload total and Response Performance total with Total Complaints.
4. For Timely Response Rate, compare the shown numerator and denominator against `timely_response_count` and `timely_response_denominator`; never divide by all complaints when `Unknown` exists.
5. Save a screenshot/PDF and record the Tableau Public URL after the values reconcile.

## Current deployment status

The local baseline and Snowflake/dbt checks are complete. The Tableau source workbook has been rebuilt from the generated aggregate marts and its Quality Reconciliation sheet shows only `PASS`. The remaining deployment step is a manual refresh and republish of the existing Tableau Public dashboard. The generated `snowflake_validation.json` is intentionally ignored by Git because it is execution evidence, not a precomputed artifact.
