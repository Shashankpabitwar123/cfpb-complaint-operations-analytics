{{ config(tags=['mart', 'tableau_export']) }}

with grouped as (
    select
        received_year,
        submitted_via,
        count(*) as complaint_volume
    from {{ ref('fct_complaints') }}
    group by 1, 2
)

select
    received_year,
    submitted_via,
    complaint_volume,
    complaint_volume / nullif(sum(complaint_volume) over (partition by received_year), 0) as complaint_share_of_year,
    dense_rank() over (partition by received_year order by complaint_volume desc) as channel_volume_rank_in_year
from grouped
order by received_year, complaint_volume desc
