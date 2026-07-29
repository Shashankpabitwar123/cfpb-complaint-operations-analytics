-- dbt data test: dashboard marts must roll up to the canonical fact volume.
with expected as (
    select count(*) as complaint_volume
    from {{ ref('fct_complaints') }}
),
actual as (
    select sum(complaint_volume) as complaint_volume
    from {{ ref('mart_monthly_operations') }}
)
select
    expected.complaint_volume as expected_volume,
    actual.complaint_volume as actual_volume
from expected cross join actual
where expected.complaint_volume <> actual.complaint_volume
