# CFPB Complaint Operations Analytics | Tableau, Snowflake, dbt, SQL

An operations analytics case study using the official CFPB Consumer Complaint Database. It turns a privacy-minimized 2023–2025 complaint extract into validated warehouse models and compact Tableau-ready aggregates.

**Current Tableau Public dashboard:** [CFPB Complaint Operations Analytics](https://public.tableau.com/views/CFPBComplaintOperationsAnalytics/OperationsOverview?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Business questions

- How did complaint workload change by month and year?
- Which product and issue categories account for the largest share of observed workload?
- What do published timely-response and known-response coverage rates look like?
- How are complaints distributed by submission channel, company, and state?
- Which patterns warrant operational attention without treating raw complaint counts as proof of company quality or consumer harm?

## Scope, grain, and privacy

| Item | Definition |
|---|---|
| Source | [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/) |
| Analysis period | Full calendar years 2023-01-01 through 2025-12-31 |
| Grain | One published complaint record per Complaint ID |
| Validated records | 9,363,711 |
| 2026 handling | Excluded because it was incomplete at retrieval |
| Privacy boundary | Consumer narratives, ZIP codes, and tags are not loaded to Snowflake or the Tableau source |

## Architecture

```text
Official CFPB CSV
  -> Python chunked preparation + initial validation
  -> Snowflake RAW.COMPLAINTS_CSV (privacy-minimized)
  -> dbt staging, dimensions, fact table, marts, and tests
  -> reconciliation checks
  -> aggregate Tableau extract workbook
  -> one Tableau Public dashboard
```

Tableau Public does **not** use a live Snowflake connection. The public dashboard is refreshed from a compact, aggregate extract generated from the Snowflake dbt marts. This is intentional and documented rather than presented as a live connection.

## Data model

`fct_complaints` holds one valid Complaint ID. Its stable keys are Complaint ID, Date received, Company, published Product/Sub-product, and State. It relates logically to:

- `dim_date`
- `dim_company`
- `dim_product`
- `dim_state`

The Tableau-facing marts are `mart_monthly_operations`, `mart_product_workload`, `mart_issue_workload`, `mart_response_performance`, `mart_channel_mix`, `mart_state_workload`, `mart_company_concentration`, and `mart_data_quality_reconciliation`.

See [the architecture and transformation log](docs/snowflake_dbt_architecture.md) and [the data dictionary](docs/data_dictionary.md).

## Selected findings

| Finding | Evidence |
|---|---:|
| Complaint workload rose sharply | 1,185,973 (2023) -> 2,734,308 (2024, +130.55%) -> 5,443,430 (2025, +99.08%) |
| Credit-reporting workload dominates | 7,578,201 complaints (80.93%) under the current published label; an older/alternate label is intentionally kept separate |
| Web is the primary intake channel | 97.24% (2023), 98.57% (2024), 99.34% (2025) |
| Timely-response rate is high | 99.55% to 99.72%, calculated as Yes / (Yes + No) |
| State counts require context | Florida, Texas, and California have the largest observed raw counts; no population denominator is used |

The findings describe observed published complaint workload. They do not measure customer satisfaction, resolution time, validated misconduct, market-adjusted company quality, or causality.

## Repository layout

```text
dbt/cfpb_complaint_operations/  Snowflake dbt project, source tests, fact, dimensions, marts
sql/                            10 reviewed analysis queries and Snowflake setup scripts
scripts/                        Preparation, Snowflake loading, reconciliation, and Tableau-export scripts
data/processed/summary/         Compact pre-warehouse validation summaries
data/exports/tableau/           Local-only aggregate dbt mart exports (ignored by Git)
tableau/                        Tableau-ready extract workbook
docs/                           KPI definitions, QA, architecture, dashboard specification, and memo
excel/                          Initial data-quality review workbook
```

The original download and row-level processed data are not committed because they total roughly 19 GB. Compact summaries, code, validation definitions, and the Tableau source workbook are included.

## Reproduce locally

1. Download the [official CFPB complaint CSV](https://files.consumerfinance.gov/ccdb/complaints.csv.zip), extract it to `data/raw/complaints.csv`, and install dependencies.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install -r requirements.txt
   ```

2. Build the local privacy-filtered extract and baseline checks.

   ```bash
   python3 scripts/prepare_data.py
   python3 scripts/build_sqlite.py
   ```

3. Create a Snowflake trial/account, copy `.env.example` to `.env`, and set your account locator, username, and password only on your own machine. A new self-service trial normally uses native password authentication; use `externalbrowser` only if your account has a configured SAML identity provider. Do not commit `.env`.

4. Run the warehouse setup/load/dbt/test/export sequence.

   ```bash
   bash scripts/run_snowflake_pipeline.sh
   ```

5. Rebuild `tableau/CFPB_Tableau_Source.xlsx` from `data/exports/tableau/` in the Codex runtime, refresh the single Tableau dashboard, apply the documented actions/filters, and publish the extract snapshot to Tableau Public. See [deployment instructions](docs/dashboard_refresh_and_publish.md).

## Validation status

| Check | Status |
|---|---|
| 2023–2025 local source validation | Complete: 9,363,711 rows, 9,363,711 unique Complaint IDs, 0 duplicate IDs |
| Initial compact-summary reconciliation | Complete: monthly and state totals reconcile to the validated record count |
| Snowflake/dbt project code | Complete and executed |
| Snowflake load, dbt run/test, and warehouse reconciliation | Complete on 2026-07-29: 9,363,711 raw/fact rows, 15 dbt models built, 31 tests passed, 6 reconciliation checks passed |
| Tableau source workbook from generated dbt mart extract | Complete: rebuilt and visually verified as a Snowflake dbt mart extract snapshot |
| Tableau Public refresh from generated dbt mart extract | Pending manual refresh and republish of the existing dashboard |

Resume and portfolio materials may accurately claim Snowflake, dbt, SQL, data-quality testing, and reconciliation for this project. Do not call the public Tableau dashboard a live Snowflake connection, and do not claim it was refreshed from this extract until the manual Tableau republish step is complete.

## Documentation

- [Data dictionary and KPI definitions](docs/data_dictionary.md)
- [Transformation log and Snowflake/dbt architecture](docs/snowflake_dbt_architecture.md)
- [Quality and reconciliation rules](docs/qa_validation.md)
- [Tableau calculation, filter, action, and publish specification](docs/tableau_build_spec.md)
- [Operational findings and recommendations](docs/operations_memo.md)
- [Source notes and limitations](docs/source_notes.md)
