# dbt project: CFPB Complaint Operations

This dbt project runs against Snowflake and creates one canonical complaint fact, four dimensions, eight Tableau-ready marts, and data-quality tests.

## Run

From the repository root, create `.dbt/profiles.yml` from `profiles.yml.example`, set the Snowflake environment variables from `.env.example`, then run:

```bash
cd dbt/cfpb_complaint_operations
dbt debug --profiles-dir ../../.dbt
dbt run --profiles-dir ../../.dbt
dbt test --profiles-dir ../../.dbt
```

Use `scripts/run_snowflake_pipeline.sh` for the full intentional raw-load, dbt, reconciliation, and export sequence.

## Models

- `stg_complaints`: type casting, standardization, and 2023–2025 filter.
- `int_complaints_enriched`: canonical derived calendar and response flags.
- `dim_*`: date, company, product, state dimensions.
- `fct_complaints`: one valid published Complaint ID.
- `mart_*`: compact measures, workload, concentration, and reconciliation tables consumed by the Tableau extract process.

## Tests

- Source Complaint ID uniqueness/not-null and Date received not-null.
- Fact/dimension keys, accepted timely-response values, and relationships.
- Source-calendar agreement and fact-to-monthly-mart volume equality.

The execution outputs are deliberately ignored; commit the model/test code and documentation, not credentials or generated warehouse artifacts.
