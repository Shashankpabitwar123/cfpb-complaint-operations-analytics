{{ config(tags=['dimension']) }}

select distinct
    product,
    sub_product
from {{ ref('int_complaints_enriched') }}
