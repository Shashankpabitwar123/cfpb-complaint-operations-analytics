-- dbt data test: source-derived calendar fields must agree with Date received.
select *
from {{ ref('stg_complaints') }}
where source_year <> year(date_received)
   or source_month_start <> date_trunc('month', date_received)::date
