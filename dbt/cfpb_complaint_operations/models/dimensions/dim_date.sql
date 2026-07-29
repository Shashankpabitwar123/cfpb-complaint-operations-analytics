{{ config(tags=['dimension']) }}

select distinct
    date_received as date_day,
    month_start,
    received_year,
    received_quarter,
    received_weekday_number,
    received_weekday
from {{ ref('int_complaints_enriched') }}
