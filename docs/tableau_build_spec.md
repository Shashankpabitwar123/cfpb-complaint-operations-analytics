# Tableau dashboard build specification

Build this only after the SQL summaries and QA checks are complete.

## Dashboard 1 — Operations overview

- KPI cards: total complaints, average monthly complaints, response coverage, timely response rate.
- Main view: monthly complaint volume line chart, 2023–2025.
- Supporting view: annual volume bars with year-over-year labels.
- Filters: year, product, state, submission channel.

## Dashboard 2 — Product and issue workload

- Horizontal bars: complaints by product.
- Drill-down or second view: top issues within selected product.
- Tooltip: complaint count, share of total, year-over-year change.
- Keep “Unknown” visible as a data-quality category.

## Dashboard 3 — Response operations

- Stacked bars: known response outcome mix by year.
- Line or bars: timely response rate by month, with the denominator shown in tooltip.
- Coverage card: percent of records with a known response outcome.
- Do not label unknown outcomes as failures.

## Dashboard 4 — Channel and geography

- Bars: complaints by submission channel.
- Ranked bars or filled map: complaints by state/territory.
- Use counts, not population-adjusted rates, unless a separate population source is added and documented.

## Design rules

- Every view must show the 2023–2025 scope and source date.
- Titles should state the metric and unit, such as “Complaints received (count)”.
- Tooltips should show numerator and denominator for rates.
- Add a visible limitations note: observed complaint workload is not market-share-adjusted quality.
