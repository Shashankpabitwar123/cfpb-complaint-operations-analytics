# Tableau build, calculations, filters, actions, and publication specification

## Scope

Maintain **one dashboard only**: `Operations Overview`. Do not create a second CFPB dashboard. The upgrade strengthens the data source, definitions, quality controls, interaction, and communication rather than adding pages.

## Tableau data source

After a successful Snowflake/dbt run, connect Tableau to `tableau/CFPB_Tableau_Source.xlsx`, which contains only the compact dbt mart snapshots:

- Monthly Operations
- Product Workload
- Issue Workload
- Response Performance
- Channel Mix
- State Workload
- Company Concentration
- Quality Reconciliation

Do not connect Tableau Public to raw complaints or claim a live Snowflake data source. The workbook is an extract snapshot generated from Snowflake dbt marts.

## Layout and views

| Zone | Source sheet | Visual | Required fields |
|---|---|---|---|
| KPI band | Monthly Operations | Total complaints, timely-response rate, known-response coverage | Complaint volume and explicit rate numerators/denominators |
| Trend | Monthly Operations | Monthly complaint volume line | `month_start`, `complaint_volume`; tooltip includes MoM change/growth and rolling three-month average |
| Workload | Product Workload | Ranked product bar chart | Product, volume, share of year, rank |
| Issue drill-down | Issue Workload | Top issues in selected product | Product, issue, volume, rank within product |
| Response | Response Performance | Timely response by year/product | Rate plus numerator and denominator in tooltip |
| Intake | Channel Mix | Submission-channel mix | Channel, volume, share |
| Geography | State Workload | Ranked state/territory bars or filled map | Raw count and share only; visible non-normalized note |
| Concentration | Company Concentration | Top companies with 100+ observed complaints | Company, volume, share, timely rate; workload only |
| QA footer | Quality Reconciliation | Pass/fail text table | Check name and status |

## Calculated fields in Tableau

Use the dbt supplied metrics where available. The following fields should be created in Tableau only when a worksheet needs an aggregate calculation:

| Field name | Tableau formula | Use |
|---|---|---|
| `Total Complaints` | `SUM([complaint_volume])` | KPI / compatible aggregate sheets |
| `Timely Response Rate` | `SUM([timely_response_count]) / NULLIF(SUM([timely_response_denominator]), 0)` | Monthly Operations or Response Performance; preserves the documented denominator |
| `Known Response Coverage Rate` | `SUM([company_response_count]) / NULLIF(SUM([complaint_volume]), 0)` | Monthly Operations |
| `Product Share of Selected Year` | `SUM([complaint_volume]) / TOTAL(SUM([complaint_volume]))` | Product bar chart; set Compute Using to Product within Year |
| `Company Complaint Share` | `SUM([complaint_volume]) / TOTAL(SUM([complaint_volume]))` | Company view; retain 100+ threshold filter |
| `MoM Growth Display` | `SUM([month_over_month_volume_growth_rate])` | Trend tooltip only; it is calculated upstream against the true prior month |

Format all rates as percentages with one decimal place, counts with separators, and null MoM metrics as `N/A` rather than zero.

## Filters and dashboard actions

1. Add `received_year` as the global filter. Apply it to every worksheet containing that field.
2. Add a Product selector on Product Workload. Add a **Filter Action** from Product Workload to Issue Workload, Response Performance, and Company Concentration; target field: `product`.
3. Add a State selection/highlight action for the geography view. Because the published data is already aggregated by differing grains, do not present State as a universal cross-sheet filter.
4. Add a Channel filter to Channel Mix only unless a compatible cross-source model is later introduced.
5. Add a `Reset selections` button that clears Product/State actions and returns the dashboard to all values.
6. In tooltips, show the time coverage, numerator/denominator for rates, and the limitation appropriate to the view.

## Labels and limitations to display

- `Scope: CFPB complaints received, full years 2023–2025 | Source: CFPB Consumer Complaint Database`
- `Observed complaint workload; not market-share-adjusted company quality or consumer harm.`
- `State values are raw counts, not population-adjusted rates.`
- `Timely response = Yes / (Yes + No); Unknown is excluded from the denominator.`
- `Company view is a workload concentration view and uses a 100-complaint threshold.`

## Refresh and publication gate

Before publishing, the Quality Reconciliation sheet must show only `PASS` and the Tableau totals must reconcile using the [QA protocol](qa_validation.md#tableau-reconciliation-protocol). Save dashboard screenshots/PDF and replace the live Tableau Public URL in the README only after this check.
