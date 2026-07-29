{{ config(tags=['mart', 'tableau_export']) }}

with monthly as (
    select
        month_start,
        received_year,
        count(*) as complaint_volume,
        count_if(is_timely_response = 1) as timely_response_count,
        count_if(has_timely_response_status = 1) as timely_response_denominator,
        count_if(has_company_response = 1) as company_response_count
    from {{ ref('fct_complaints') }}
    group by 1, 2
),

with_comparisons as (
    select
        *,
        lag(complaint_volume) over (order by month_start) as prior_month_complaint_volume,
        avg(complaint_volume) over (
            order by month_start rows between 2 preceding and current row
        ) as rolling_3_month_avg_complaint_volume
    from monthly
)

select
    month_start,
    received_year,
    complaint_volume,
    timely_response_count,
    timely_response_denominator,
    timely_response_count / nullif(timely_response_denominator, 0) as timely_response_rate,
    company_response_count,
    company_response_count / nullif(complaint_volume, 0) as company_response_coverage_rate,
    prior_month_complaint_volume,
    complaint_volume - prior_month_complaint_volume as month_over_month_volume_change,
    (complaint_volume / nullif(prior_month_complaint_volume, 0)) - 1 as month_over_month_volume_growth_rate,
    rolling_3_month_avg_complaint_volume
from with_comparisons
order by month_start
