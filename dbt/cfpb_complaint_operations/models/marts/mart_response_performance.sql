{{ config(tags=['mart', 'tableau_export']) }}

select
    received_year,
    product,
    company_response_to_consumer,
    count(*) as complaint_volume,
    count_if(is_timely_response = 1) as timely_response_count,
    count_if(has_timely_response_status = 1) as timely_response_denominator,
    count_if(has_company_response = 1) as company_response_count,
    count_if(is_timely_response = 1) / nullif(count_if(has_timely_response_status = 1), 0) as timely_response_rate,
    count_if(has_company_response = 1) / nullif(count(*), 0) as company_response_coverage_rate
from {{ ref('fct_complaints') }}
group by 1, 2, 3
order by received_year, complaint_volume desc
