{{ config(tags=['dimension']) }}

select distinct
    state_code
from {{ ref('int_complaints_enriched') }}
