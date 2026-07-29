{{ config(tags=['intermediate']) }}

with complaints as (
    select *
    from {{ ref('stg_complaints') }}
    where is_valid_complaint
)

select
    complaint_id,
    date_received,
    date_trunc('month', date_received)::date as month_start,
    year(date_received) as received_year,
    quarter(date_received) as received_quarter,
    dayofweekiso(date_received) as received_weekday_number,
    dayname(date_received) as received_weekday,
    product,
    sub_product,
    issue,
    sub_issue,
    company_public_response,
    company,
    state_code,
    submitted_via,
    date_sent_to_company,
    company_response_to_consumer,
    timely_response,
    iff(company_response_to_consumer <> 'Unknown', 1, 0) as has_company_response,
    iff(timely_response in ('Yes', 'No'), 1, 0) as has_timely_response_status,
    iff(timely_response = 'Yes', 1, 0) as is_timely_response,
    source_year,
    source_month_start,
    source_has_company_response,
    source_timely_response_flag,
    loaded_at
from complaints
