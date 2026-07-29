{{ config(tags=['mart', 'tableau_export']) }}

with grouped as (
    select
        received_year,
        product,
        count(*) as complaint_volume,
        count_if(is_timely_response = 1) as timely_response_count,
        count_if(has_timely_response_status = 1) as timely_response_denominator
    from {{ ref('fct_complaints') }}
    group by 1, 2
)

select
    received_year,
    product,
    complaint_volume,
    complaint_volume / nullif(sum(complaint_volume) over (partition by received_year), 0) as complaint_share_of_year,
    dense_rank() over (partition by received_year order by complaint_volume desc) as product_volume_rank_in_year,
    timely_response_count,
    timely_response_denominator,
    timely_response_count / nullif(timely_response_denominator, 0) as timely_response_rate
from grouped
order by received_year, complaint_volume desc
