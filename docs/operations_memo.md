# CFPB Complaint Operations Analytics — findings and recommendations

## Scope

This analysis covers 9,363,711 published CFPB complaint records received from 2023-01-01 through 2025-12-31. It measures observed published complaint workload and source response-record patterns. It does not measure causality, customer satisfaction, resolution time, validated misconduct, monetary harm, or market-share-adjusted company quality.

## Operational findings and recommended actions

| Finding | Magnitude | Operational implication | Limitation | Recommended action |
|---|---:|---|---|---|
| Workload grew sharply across the full-year comparison window. | 1,185,973 complaints (2023) -> 2,734,308 (2024, +130.55%) -> 5,443,430 (2025, +99.08%). | Intake, classification, and investigation capacity must plan for sustained volume growth rather than a single spike. | Complaint records are observed published workload, not all consumer issues in the market. | Create a monthly capacity/triage review using volume, MoM change, and rolling three-month volume. |
| Credit-reporting categories dominate reported workload. | The current `Credit reporting or other personal consumer reports` label has 7,578,201 records (80.93%); a separate alternate label has 557,760 (5.96%). | Work queues and root-workload diagnostics should prioritize credit-reporting issues. | Source taxonomy changed/varies across labels; merging labels without a documented bridge would distort reporting. | Maintain product-specific operating queues and create a reviewed taxonomy crosswalk before any combined credit-reporting KPI is published. |
| A small set of published issue categories drives most observed workload. | Largest product-issue combinations: incorrect information on a report (4,185,700), improper use of a report (1,919,581), and problems with an investigation (1,396,144). | High-volume issue themes are practical candidates for monitoring rules, knowledge content, and routing review. | Issue labels describe the filed complaint; they do not prove an underlying root cause. | Track top issue ranks by product/month and require qualitative review before changing policy or assigning cause. |
| Digital intake is overwhelmingly web-based. | Web share: 97.24% (2023), 98.57% (2024), 99.34% (2025). | Web-form availability, validation, accessibility, and routing have outsized operational importance. | Channel values describe submission channel, not the consumer journey or channel preference in the broader population. | Add web intake health monitoring and use channel mix as a trigger for form-quality and capacity reviews. |
| Published timely-response rates are high, while state and company values need context. | Timely response: 99.57% (2023), 99.72% (2024), 99.55% (2025); Florida, Texas, and California have highest raw state counts. | Timely-response monitoring should focus on exceptions and data coverage; geographic/company comparisons need controlled context. | Timely response is a CFPB source indicator, and raw state/company counts lack population, customer-base, product-mix, and market-share denominators. | Display explicit timely-rate denominators, keep `Unknown` visible, apply the 100-complaint company threshold, and avoid per-capita or quality claims without new documented data. |

## KPI definitions used in communication

- **Complaint volume:** count of unique Complaint IDs; local validation found no duplicate IDs in the 2023–2025 extract.
- **Timely-response rate:** `Yes / (Yes + No)` for the CFPB `Timely response?` field; `Unknown` is excluded from the denominator.
- **Known company-response coverage:** known company response count divided by complaint volume. It does not evaluate response quality.
- **Segment share:** product/channel/state/company observed complaint volume divided by all complaints in the same year. It is not market share.

## Communication guardrails

- Use “associated with,” “observed,” and “workload” language.
- Do not claim that a company, state, product, or channel caused a complaint outcome.
- Do not invent resolution time, satisfaction, retention, or consumer-harm measures.
- Keep the stated 2023–2025 coverage, rate denominator, and raw-count limitations visible in the dashboard and portfolio README.
