{{ config(tags=['mart', 'quality']) }}

with source_checks as (
    select
        count(*) as raw_row_count,
        count(distinct try_to_number(regexp_replace(complaint_id_raw, '\\.0$', ''))) as raw_distinct_complaint_id_count,
        count_if(try_to_number(regexp_replace(complaint_id_raw, '\\.0$', '')) is null) as raw_missing_complaint_id_count,
        count_if(try_to_date(date_received_raw) is null) as raw_invalid_date_count
    from {{ source('raw', 'complaints_csv') }}
),
fact_checks as (
    select
        count(*) as fact_row_count,
        count(distinct complaint_id) as fact_distinct_complaint_id_count,
        count_if(complaint_id is null) as fact_missing_complaint_id_count,
        count_if(date_received is null) as fact_invalid_date_count
    from {{ ref('fct_complaints') }}
)

select
    'Raw row count equals fact row count' as check_name,
    s.raw_row_count as expected_value,
    f.fact_row_count as actual_value,
    f.fact_row_count - s.raw_row_count as difference_value,
    iff(f.fact_row_count = s.raw_row_count, 'PASS', 'FAIL') as status
from source_checks s cross join fact_checks f

union all

select
    'Raw distinct Complaint ID count equals fact row count',
    s.raw_distinct_complaint_id_count,
    f.fact_row_count,
    f.fact_row_count - s.raw_distinct_complaint_id_count,
    iff(f.fact_row_count = s.raw_distinct_complaint_id_count, 'PASS', 'FAIL')
from source_checks s cross join fact_checks f

union all

select
    'Missing Complaint IDs in fact',
    0,
    f.fact_missing_complaint_id_count,
    f.fact_missing_complaint_id_count,
    iff(f.fact_missing_complaint_id_count = 0, 'PASS', 'FAIL')
from fact_checks f

union all

select
    'Invalid Date received values in fact',
    0,
    f.fact_invalid_date_count,
    f.fact_invalid_date_count,
    iff(f.fact_invalid_date_count = 0, 'PASS', 'FAIL')
from fact_checks f
