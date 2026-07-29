{{ config(tags=['fact']) }}

select
    complaint_id,
    date_received,
    month_start,
    received_year,
    received_quarter,
    received_weekday_number,
    received_weekday,
    product,
    sub_product,
    issue,
    sub_issue,
    company_public_response,
    company as company_name,
    state_code,
    submitted_via,
    date_sent_to_company,
    company_response_to_consumer,
    timely_response,
    has_company_response,
    has_timely_response_status,
    is_timely_response,
    loaded_at
from {{ ref('int_complaints_enriched') }}
