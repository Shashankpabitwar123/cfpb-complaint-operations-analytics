# Data dictionary and KPI definitions

## Scope and exclusions

The source/fact grain is one published CFPB complaint per Complaint ID, received from 2023-01-01 through 2025-12-31. The 2026 records available at retrieval were incomplete and are excluded. Consumer narratives, ZIP codes, and tags are excluded from Snowflake and Tableau outputs. Missing categorical values are retained as `Unknown`; they are not dropped.

## Source and transformed fields

| Source field | Warehouse field | Definition and use |
|---|---|---|
| Date received | `date_received`, `month_start`, `received_year`, `received_quarter`, `received_weekday` | CFPB receipt date and calendar dimensions for trends |
| Product | `product` | Published product category for workload segmentation |
| Sub-product | `sub_product` | Published sub-product; retained without undocumented category consolidation |
| Issue | `issue` | Published issue category for root-workload analysis |
| Sub-issue | `sub_issue` | Detailed issue; supports drill-down only |
| Company public response | `company_public_response` | Published public response field; not customer satisfaction |
| Company | `company_name` | Company shown in the complaint; used only for observed workload concentration |
| State | `state_code` | State/territory code; raw counts, never per-capita rates in this project |
| Submitted via | `submitted_via` | Intake channel for channel-mix analysis |
| Date sent to company | `date_sent_to_company` | Operational timing context; not used to invent resolution-time measures |
| Company response to consumer | `company_response_to_consumer` | Published response outcome mix |
| Timely response? | `timely_response`, `is_timely_response`, `has_timely_response_status` | `Yes`, `No`, or `Unknown`; explicitly controls the timely-rate denominator |
| Complaint ID | `complaint_id` | Stable record key and deduplication key |
| Derived source year/month/flags | source-audit fields | Checked against values derived from Date received or response fields; not used as the source of truth |

## Warehouse model dictionary

| Model | Grain | Purpose |
|---|---|---|
| `raw.complaints_csv` | Prepared source row | Privacy-minimized landed extract; 2023–2025 only |
| `stg_complaints` | Valid source row | Type casts, `Unknown` treatment, analysis-window filter, validity flag |
| `int_complaints_enriched` | Valid Complaint ID | Calendar and response flags used consistently downstream |
| `dim_date` | Date received | Date attributes |
| `dim_company` | Company name | Stable company dimension values |
| `dim_product` | Product + sub-product | Published product taxonomy values |
| `dim_state` | State/territory code | Geographic dimension values |
| `fct_complaints` | Complaint ID | Canonical one-row-per-complaint fact table |
| `mart_monthly_operations` | Month | Volume, response rates, month-over-month, rolling three-month volume |
| `mart_product_workload` | Year + product | Product workload, share, rank, timely rate |
| `mart_issue_workload` | Year + product + issue | Issue workload, share within product, rank |
| `mart_response_performance` | Year + product + response outcome | Response-volume and timely/coverage metrics |
| `mart_channel_mix` | Year + submission channel | Channel volume, share, rank |
| `mart_state_workload` | Year + state/territory | Raw geographic volume, share, rank, timely rate |
| `mart_company_concentration` | Year + company + product | Observed company workload concentration, explicit 100-complaint threshold band |
| `mart_data_quality_reconciliation` | Check | Source-to-fact and fact-to-mart comparison results |

## KPI definitions

| KPI | Formula | Denominator / interpretation |
|---|---|---|
| Complaint volume | `COUNT(*)` in `fct_complaints` | One valid Complaint ID equals one complaint. There are no duplicates in the validated local extract. |
| Month-over-month volume change | Current-month volume − prior-month volume | First month has no prior-month comparison. |
| Month-over-month volume growth rate | `(Current-month volume / prior-month volume) − 1` | Null when prior month is zero or absent. |
| Year-over-year volume growth rate | `(Current-year volume / prior-year volume) − 1` | Null for the first analysis year. |
| Product / channel / state complaint share | Segment volume / total volume in the same year | Share of observed complaints, not market share. |
| Timely-response rate | `timely_response_count / timely_response_denominator` | Denominator is records coded `Yes` or `No`; `Unknown` is excluded, never treated as late. |
| Known company-response coverage | `company_response_count / complaint_volume` | Indicates whether a response field is known, not response quality. |
| Company complaint concentration | Company complaint volume / year complaint volume | Use the 100-complaint threshold band; not an assessment of company fault or consumer satisfaction. |
| State complaint pattern | State raw complaint volume / year complaint volume | No population or account-base denominator is loaded; do not call it a rate. |

## Tableau filters and exclusions

- Default date coverage: 2023 through 2025 only.
- `Unknown` remains selectable/visible for categorical fields.
- Product labels are kept as published. The two credit-reporting labels are not combined without a documented taxonomy bridge.
- Company comparisons should retain the `100+ complaints` threshold band.
- No customer narrative, ZIP code, or tags are exposed to the Tableau source workbook.
