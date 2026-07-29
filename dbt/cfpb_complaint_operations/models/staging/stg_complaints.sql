{{ config(tags=['staging', 'privacy_minimized']) }}

with source_rows as (
    select *
    from {{ source('raw', 'complaints_csv') }}
),

standardized as (
    select
        try_to_number(regexp_replace(complaint_id_raw, '\\.0$', '')) as complaint_id,
        try_to_date(date_received_raw) as date_received,
        coalesce(nullif(trim(product_raw), ''), 'Unknown') as product,
        coalesce(nullif(trim(sub_product_raw), ''), 'Unknown') as sub_product,
        coalesce(nullif(trim(issue_raw), ''), 'Unknown') as issue,
        coalesce(nullif(trim(sub_issue_raw), ''), 'Unknown') as sub_issue,
        coalesce(nullif(trim(company_public_response_raw), ''), 'Unknown') as company_public_response,
        coalesce(nullif(trim(company_raw), ''), 'Unknown') as company,
        coalesce(nullif(upper(trim(state_raw)), ''), 'Unknown') as state_code,
        coalesce(nullif(trim(submitted_via_raw), ''), 'Unknown') as submitted_via,
        try_to_date(date_sent_to_company_raw) as date_sent_to_company,
        coalesce(nullif(trim(company_response_to_consumer_raw), ''), 'Unknown') as company_response_to_consumer,
        case
            when upper(trim(timely_response_raw)) = 'YES' then 'Yes'
            when upper(trim(timely_response_raw)) = 'NO' then 'No'
            else 'Unknown'
        end as timely_response,
        try_to_number(year_raw) as source_year,
        try_to_date(concat(month_start_raw, '-01')) as source_month_start,
        case
            when upper(trim(has_company_response_raw)) in ('1', 'TRUE', 'YES') then 1
            when upper(trim(has_company_response_raw)) in ('0', 'FALSE', 'NO') then 0
            else null
        end as source_has_company_response,
        case
            when upper(trim(timely_response_flag_raw)) = 'YES' then 'Yes'
            when upper(trim(timely_response_flag_raw)) = 'NO' then 'No'
            else 'Unknown'
        end as source_timely_response_flag,
        loaded_at
    from source_rows
)

select
    *,
    iff(complaint_id is not null and date_received is not null, true, false) as is_valid_complaint
from standardized
where date_received >= '2023-01-01'::date
  and date_received < '2026-01-01'::date
