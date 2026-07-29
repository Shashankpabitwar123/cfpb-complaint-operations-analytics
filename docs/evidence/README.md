# Published dashboard evidence

These files document the final Tableau Public release on 2026-07-29.

- `CFPB_Operations_Overview.pdf` is the exported Operations Overview dashboard.
- `CFPB_Operations_Overview.png` is a rendered review image of that PDF.
- `../../tableau/CFPB_Complaint_Operations_Analytics_Snowflake_dbt_Extract.twbx` is the packaged workbook used for the release.

The workbook uses a compact, aggregate Tableau extract generated from the Snowflake dbt marts. It is not a live Snowflake connection. The dashboard labels the 2023-2025 coverage, 9.36M validated complaints, the +99.1% 2025 year-over-year volume change, and the raw-count limitation for the state map.
