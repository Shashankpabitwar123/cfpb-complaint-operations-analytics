# CFPB Complaint Operations Analytics — findings memo

## Scope

This memo describes 9,363,711 published CFPB complaint records received from 2023-01-01 through 2025-12-31. It describes observed complaint workload and published response-record patterns; it does not measure market-share-adjusted company quality or causal performance.

## Executive findings

1. **Observed workload grew rapidly.** Complaint volume increased from 1,185,973 records in 2023 to 2,734,308 in 2024 (+130.55%) and 5,443,430 in 2025 (+99.08%). The monthly peak was December 2023 (123,067), December 2024 (303,982), and October 2025 (519,813).
2. **Credit reporting dominates the work queue.** The current label `Credit reporting or other personal consumer reports` represents 7,578,201 records (80.93%). A second, older/alternate credit-reporting label contributes another 557,760 records (5.96%). These labels should remain separate in headline reporting unless a documented taxonomy bridge is added.
3. **The largest reported issues are concentrated in reporting accuracy and use.** The three largest product–issue combinations are incorrect information on a report (4,185,700), improper use of a report (1,919,581), and problems with an investigation into an existing problem (1,396,144), all under the dominant credit-reporting product label.
4. **Published response coverage and reported timeliness are high.** Known public-response coverage was 100.00% in 2023 and 2024 and 99.99% in 2025. Timely-response rate, calculated as `Yes / (Yes + No)`, was 99.57%, 99.72%, and 99.55% respectively. This is a source-field indicator, not a consumer-satisfaction measure.
5. **Web is the primary intake channel.** Web submissions represented 97.24% of volume in 2023, 98.57% in 2024, and 99.34% in 2025. This supports prioritizing digital intake capacity and web-form quality monitoring.
6. **Highest observed state counts were Florida (1,340,357), Texas (1,291,762), and California (896,823).** These are raw counts only; they must not be interpreted as population-adjusted complaint rates.

## Operations implications

- Plan staffing and triage capacity around the sharply rising credit-reporting workload and the high-volume monthly peaks.
- Create a taxonomy bridge before making an all-time credit-reporting product total, because source categories reflect different labels.
- Monitor digital intake flow, validation, and routing because web contributes nearly all submissions.
- Pair state counts with a documented denominator, such as population or active accounts, before making geographic performance claims.

## Metric definitions

- **Complaint volume:** count of unique Complaint IDs. The data-quality check found no duplicates in the 2023–2025 extract.
- **Response coverage:** records with a known company public response divided by all records.
- **Timely-response rate:** timely `Yes` divided by all known timely outcomes (`Yes` plus `No`).
- **Product/issue workload:** count of unique Complaint IDs grouped by published CFPB category labels.

## Limitations

- The CFPB database is not a statistical sample; complaint counts are not market-share-adjusted quality measures.
- Published records can be affected by the CFPB publication process and source taxonomy changes.
- Results describe complaints received, not validated misconduct, monetary harm, resolution quality, or consumer satisfaction.
