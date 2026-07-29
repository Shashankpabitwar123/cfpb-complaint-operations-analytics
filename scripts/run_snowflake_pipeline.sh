#!/usr/bin/env bash
# Reproducible local sequence. Run only after creating the Snowflake objects and
# setting environment variables from .env.example. This script never creates a
# credential file in Git and does not publish to Tableau Public automatically.
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dbt_root="$project_root/dbt/cfpb_complaint_operations"
profile_dir="$project_root/.dbt"
skip_load=false

if [[ "${1:-}" == "--skip-load" ]]; then
  skip_load=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--skip-load]" >&2
  exit 1
fi

if [[ ! -f "$project_root/.env" ]]; then
  echo "Create .env from .env.example and set Snowflake account/user first." >&2
  exit 1
fi

if ! command -v dbt >/dev/null 2>&1; then
  echo "Install the documented Python dependencies first: python3 -m pip install -r requirements.txt" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source "$project_root/.env"
set +a

mkdir -p "$profile_dir"
cp "$dbt_root/profiles.yml.example" "$profile_dir/profiles.yml"

if [[ "$skip_load" == false ]]; then
  python3 "$project_root/scripts/load_to_snowflake.py" --replace
fi
(
  cd "$dbt_root"
  dbt debug --profiles-dir "$profile_dir"
  dbt run --profiles-dir "$profile_dir"
  dbt test --profiles-dir "$profile_dir"
)
python3 "$project_root/scripts/validate_snowflake_pipeline.py"
python3 "$project_root/scripts/export_tableau_marts.py"

echo "Snowflake/dbt pipeline completed. Rebuild tableau/CFPB_Tableau_Source.xlsx from data/exports/tableau in Codex, then refresh and republish the single Tableau Public dashboard."
