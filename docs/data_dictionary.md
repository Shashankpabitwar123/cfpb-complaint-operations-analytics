# Data dictionary

The working table has one row per CFPB Complaint ID for the 2023–2025 analysis window.

| Field | Definition | Use |
|---|---|---|
| Date received | Date CFPB received the complaint | Time-series analysis |
| Product | CFPB product category | Workload segmentation |
| Sub-product | More detailed product category | Drill-down |
| Issue | Complaint issue category | Root-workload analysis |
| Sub-issue | Detailed issue category | Drill-down |
| Company public response | Public response status | Response coverage |
| Company | Company identified in the complaint | Company workload |
| State | Consumer state/territory value | Geography |
| ZIP code | Consumer ZIP code as published | Optional geography; not used for personal profiling |
| Tags | CFPB tag values | Optional segmentation |
| Submitted via | Submission channel | Channel mix |
| Date sent to company | Date complaint was sent to company | Operational timing context |
| Company response to consumer | Response outcome | Outcome mix |
| Timely response? | CFPB timely-response indicator | Timeliness KPI |
| Complaint ID | Unique published complaint identifier | Record grain and deduplication |
| year | Derived calendar year from Date received | Year comparison |
| month_start | Derived YYYY-MM month key | Monthly trend |
| has_company_response | Derived flag for known public response | Response coverage |
| timely_response_flag | Derived Yes/No flag; blank when source value is not known | Timely response rate denominator |

Null/blank category values are retained as `Unknown` in the working extract so that missingness does not silently disappear from counts.
