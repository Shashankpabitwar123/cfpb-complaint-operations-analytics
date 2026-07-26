# CFPB Complaint Operations Analytics

Interactive Tableau case study of consumer-complaint operations using the official Consumer Financial Protection Bureau (CFPB) Consumer Complaint Database.

**Live dashboard:** [CFPB Complaint Operations Analytics on Tableau Public](https://public.tableau.com/views/CFPBComplaintOperationsAnalytics/OperationsOverview?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Business objective

Analyze how complaint operations changed from 2023 through 2025 and identify the product, geographic, and response-performance patterns that matter most for an operations team.

## Dashboard

The Tableau dashboard includes:

- Monthly complaint-volume trend
- Product workload ranking
- Complaint volume by state (raw counts)
- Timely-response rate by year

## Key findings

| Finding | Result |
|---|---:|
| Validated complaints analyzed | 9,363,711 |
| 2023 complaint volume | 1,185,973 |
| 2024 year-over-year growth | 130.55% |
| 2025 year-over-year growth | 99.08% |
| Largest product category | Credit reporting or other personal consumer reports (7,578,201; 80.93%) |
| Highest-volume state (raw count) | Florida (1,340,357) |
| Timely-response rate range | 99.55%–99.72% |

## Scope and methodology

- **Source:** [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)
- **Analysis period:** January 1, 2023–December 31, 2025
- **Record grain:** One published complaint record per Complaint ID
- **2026 exclusion:** 2026 was incomplete at retrieval, so it was excluded from year-over-year comparisons.
- **Privacy:** Consumer complaint narratives were excluded from all working and public project artifacts.
- **Data preparation:** Chunked Python processing, data-type normalization, duplicate-ID validation, and SQLite summary generation.

The analysis uses observed CFPB complaint workload. It does not treat complaint counts as market-share-adjusted measures of company quality or consumer harm.

## Repository contents

```text
data/processed/summary/  Compact CSV tables used by the dashboard
docs/                    Data dictionary, validation record, source notes, and operations memo
excel/                   Data-quality review workbook
scripts/                 Reproducible Python data-preparation and SQLite-summary scripts
sql/                     Analysis queries
tableau/                 Tableau-ready Excel source workbook
```

The raw CFPB download and row-level processed files are deliberately excluded from GitHub because they total roughly 19 GB. The compact summary tables, source workbook, scripts, and validation evidence are included.

## Reproduce the analysis

1. Download the [official CFPB complaint CSV](https://files.consumerfinance.gov/ccdb/complaints.csv.zip) and extract it to `data/raw/complaints.csv`.
2. Create a Python environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Generate the filtered extract and QA workbook:

   ```bash
   python scripts/prepare_data.py
   ```

4. Build the SQLite analysis layer and dashboard-ready summaries:

   ```bash
   python scripts/build_sqlite.py
   ```

5. Open `tableau/CFPB_Tableau_Source.xlsx` in Tableau Public, or use the included dashboard-ready CSVs. See [`docs/tableau_build_spec.md`](docs/tableau_build_spec.md) for the worksheet design.

## Validation

| Check | Result |
|---|---:|
| Processed records | 9,363,711 |
| Unique Complaint IDs | 9,363,711 |
| Duplicate Complaint IDs | 0 |
| Monthly periods | 36 |
| Narrative data included | No |
| Monthly and state totals reconciled | Yes |

See [`docs/qa_validation.md`](docs/qa_validation.md) for the full validation record and [`docs/source_notes.md`](docs/source_notes.md) for the source and interpretation caveats.

## Important interpretation notes

- CFPB states that the database is not a statistical sample; counts should not be interpreted as market-share-adjusted quality rankings.
- State values are raw complaint counts, not population-adjusted rates.
- The two credit-reporting product labels are intentionally kept separate because they originate from different source taxonomy labels; they are not combined without a documented mapping.
