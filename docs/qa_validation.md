# Validation record

## Independent checks completed

| Check | Result |
|---|---:|
| Processed rows | 9,363,711 |
| Unique Complaint IDs | 9,363,711 |
| Duplicate Complaint IDs | 0 |
| Date range | 2023-01-01 to 2025-12-31 |
| Monthly periods | 36 |
| Timely-response values | `Yes` and `No` only |
| Invalid derived timely flags | 0 |
| Consumer complaint narrative in processed extract | No |
| Monthly-summary total | 9,363,711 |
| State-summary total | 9,363,711 |

## Reconciliation notes

- All dashboard-facing complaint counts use the same validated record grain: one row per Complaint ID.
- The response-performance rate uses only records with known timely-response values in its denominator; the denominator is exported with the rate.
- `Unknown` remains visible for missing categorical fields rather than being dropped from aggregate counts.
