# Snowflake execution, Tableau refresh, and publication checklist

This project requires user-owned Snowflake and Tableau sessions for deployment. No account password, token, or private URL should be pasted into the repository or chat.

## 1. Bootstrap Snowflake once

1. Create or sign in to a Snowflake account/trial.
2. Copy `.env.example` to `.env` and set your account locator and username. For this one bootstrap run only, set `SNOWFLAKE_ROLE=ACCOUNTADMIN`.
3. Run the setup and initial load with external-browser authentication:

   ```bash
   python3 scripts/load_to_snowflake.py --apply-setup --replace
   ```

4. The setup script automatically grants the newly created `CFPB_PORTFOLIO_ROLE` to the current user. Change `.env` to `SNOWFLAKE_ROLE=CFPB_PORTFOLIO_ROLE` afterward. Keep `SNOWFLAKE_AUTHENTICATOR=externalbrowser` unless your organization requires another approved sign-in method.

## 2. Execute and validate the pipeline

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
bash scripts/run_snowflake_pipeline.sh --skip-load
```

Expected evidence:

- `dbt debug` succeeds.
- `dbt run` builds the staging, dimensions, fact, and marts.
- `dbt test` passes.
- `scripts/validate_snowflake_pipeline.py` writes a `PASS` JSON result.
- `scripts/export_tableau_marts.py` writes eight compact aggregate CSVs under `data/exports/tableau/`.

If the bootstrap upload is interrupted, resolve the error and intentionally rerun `python3 scripts/load_to_snowflake.py --replace`; do not assume a partially loaded table is valid.

## 3. Rebuild the Tableau source workbook

Run the existing `scripts/build_tableau_source.mjs` in the Codex/runtime environment after the export files exist. Its `Read Me` sheet must say `Snowflake dbt mart extract snapshot`, not `Legacy local-summary fallback`.

## 4. Refresh the one Tableau dashboard

1. Open the existing Tableau workbook/dashboard, not a new dashboard project.
2. Replace/refresh the data source using `tableau/CFPB_Tableau_Source.xlsx`.
3. Apply every field, filter, action, tooltip, and limitation listed in [the Tableau build specification](tableau_build_spec.md).
4. Use the [Tableau reconciliation protocol](qa_validation.md#tableau-reconciliation-protocol).
5. Export a dashboard PDF and screenshots for the repository.

## 5. Publish responsibly

Publish the refreshed **extract** to Tableau Public and copy the final dashboard URL into the README. Tableau Public cannot provide a live Snowflake connection, so do not label the dashboard as live/auto-refreshing from Snowflake. If live Snowflake connectivity is later required, use a Tableau Cloud/Server/Creator workflow and document its access/security choices separately.
