{{ config(tags=['dimension']) }}

select distinct
    company as company_name
from {{ ref('int_complaints_enriched') }}
