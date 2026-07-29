{{ config(tags=['mart', 'tableau_export']) }}

with grouped as (
    select
        received_year,
        product,
        issue,
        count(*) as complaint_volume
    from {{ ref('fct_complaints') }}
    group by 1, 2, 3
)

select
    received_year,
    product,
    issue,
    complaint_volume,
    complaint_volume / nullif(sum(complaint_volume) over (partition by received_year, product), 0) as issue_share_within_product,
    dense_rank() over (
        partition by received_year, product order by complaint_volume desc
    ) as issue_volume_rank_within_product
from grouped
order by received_year, product, complaint_volume desc
