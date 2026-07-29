-- CFPB Complaint Operations Analytics | reviewed Snowflake SQL
-- Prerequisite: run the dbt project so CFPB_ANALYTICS.ANALYTICS contains the fact and marts.
-- Complaint grain: one published CFPB record per Complaint ID.
-- Scope: full calendar years 2023-2025. 2026 is intentionally excluded as partial.

USE DATABASE CFPB_ANALYTICS;
USE SCHEMA ANALYTICS;

-- 01. Source-to-fact volume reconciliation by analysis year.
SELECT
    received_year,
    COUNT(*) AS complaint_volume,
    COUNT(DISTINCT complaint_id) AS distinct_complaint_ids,
    COUNT(*) - COUNT(DISTINCT complaint_id) AS duplicate_complaint_id_rows
FROM fct_complaints
GROUP BY 1
ORDER BY 1;

-- 02. Monthly complaint volume with month-over-month change and growth rate.
WITH monthly AS (
    SELECT
        month_start,
        COUNT(*) AS complaint_volume
    FROM fct_complaints
    GROUP BY 1
),
compared AS (
    SELECT
        month_start,
        complaint_volume,
        LAG(complaint_volume) OVER (ORDER BY month_start) AS prior_month_complaint_volume
    FROM monthly
)
SELECT
    month_start,
    complaint_volume,
    complaint_volume - prior_month_complaint_volume AS month_over_month_volume_change,
    (complaint_volume / NULLIF(prior_month_complaint_volume, 0)) - 1 AS month_over_month_volume_growth_rate
FROM compared
ORDER BY month_start;

-- 03. Annual complaint volume with year-over-year comparison.
WITH annual AS (
    SELECT
        received_year,
        COUNT(*) AS complaint_volume
    FROM fct_complaints
    GROUP BY 1
)
SELECT
    received_year,
    complaint_volume,
    LAG(complaint_volume) OVER (ORDER BY received_year) AS prior_year_complaint_volume,
    (complaint_volume / NULLIF(LAG(complaint_volume) OVER (ORDER BY received_year), 0)) - 1
        AS year_over_year_volume_growth_rate
FROM annual
ORDER BY received_year;

-- 04. Product workload and share within each year, ranked by volume.
WITH product_year AS (
    SELECT
        received_year,
        product,
        COUNT(*) AS complaint_volume
    FROM fct_complaints
    GROUP BY 1, 2
)
SELECT
    received_year,
    product,
    complaint_volume,
    complaint_volume / NULLIF(SUM(complaint_volume) OVER (PARTITION BY received_year), 0)
        AS complaint_share_of_year,
    DENSE_RANK() OVER (PARTITION BY received_year ORDER BY complaint_volume DESC)
        AS product_volume_rank_in_year
FROM product_year
ORDER BY received_year, complaint_volume DESC;

-- 05. Highest-volume issues within each product. The CASE label prevents
-- over-interpreting low-volume combinations as operational priorities.
WITH issue_workload AS (
    SELECT
        received_year,
        product,
        issue,
        COUNT(*) AS complaint_volume
    FROM fct_complaints
    GROUP BY 1, 2, 3
)
SELECT
    received_year,
    product,
    issue,
    complaint_volume,
    CASE
        WHEN complaint_volume >= 10000 THEN 'High-volume issue'
        WHEN complaint_volume >= 1000 THEN 'Moderate-volume issue'
        ELSE 'Low-volume issue'
    END AS volume_band,
    DENSE_RANK() OVER (
        PARTITION BY received_year, product ORDER BY complaint_volume DESC
    ) AS issue_volume_rank_within_product
FROM issue_workload
ORDER BY received_year, product, complaint_volume DESC;

-- 06. Timely-response and known-response coverage with explicit denominators.
SELECT
    received_year,
    COUNT(*) AS complaint_volume,
    COUNT_IF(is_timely_response = 1) AS timely_response_count,
    COUNT_IF(has_timely_response_status = 1) AS timely_response_denominator,
    COUNT_IF(is_timely_response = 1) / NULLIF(COUNT_IF(has_timely_response_status = 1), 0)
        AS timely_response_rate,
    COUNT_IF(has_company_response = 1) AS known_company_response_count,
    COUNT_IF(has_company_response = 1) / NULLIF(COUNT(*), 0)
        AS known_company_response_coverage_rate
FROM fct_complaints
GROUP BY 1
ORDER BY 1;

-- 07. Submission-channel mix and rank within each year.
WITH channel_year AS (
    SELECT
        received_year,
        submitted_via,
        COUNT(*) AS complaint_volume
    FROM fct_complaints
    GROUP BY 1, 2
)
SELECT
    received_year,
    submitted_via,
    complaint_volume,
    complaint_volume / NULLIF(SUM(complaint_volume) OVER (PARTITION BY received_year), 0)
        AS complaint_share_of_year,
    DENSE_RANK() OVER (PARTITION BY received_year ORDER BY complaint_volume DESC)
        AS channel_volume_rank_in_year
FROM channel_year
ORDER BY received_year, complaint_volume DESC;

-- 08. Company complaint concentration for companies with at least 100 complaints.
-- This is workload concentration, not a customer-satisfaction or fault measure.
WITH company_year AS (
    SELECT
        received_year,
        company_name,
        COUNT(*) AS complaint_volume,
        COUNT_IF(is_timely_response = 1) / NULLIF(COUNT_IF(has_timely_response_status = 1), 0)
            AS timely_response_rate
    FROM fct_complaints
    GROUP BY 1, 2
)
SELECT
    received_year,
    company_name,
    complaint_volume,
    complaint_volume / NULLIF(SUM(complaint_volume) OVER (PARTITION BY received_year), 0)
        AS complaint_share_of_year,
    timely_response_rate,
    DENSE_RANK() OVER (PARTITION BY received_year ORDER BY complaint_volume DESC)
        AS company_volume_rank_in_year
FROM company_year
WHERE complaint_volume >= 100
ORDER BY received_year, complaint_volume DESC;

-- 09. State complaint patterns by raw volume. No population denominator is loaded,
-- so this query must not be labeled a per-capita or state-normalized comparison.
WITH state_year AS (
    SELECT
        received_year,
        state_code,
        COUNT(*) AS complaint_volume
    FROM fct_complaints
    GROUP BY 1, 2
)
SELECT
    received_year,
    state_code,
    complaint_volume,
    complaint_volume / NULLIF(SUM(complaint_volume) OVER (PARTITION BY received_year), 0)
        AS complaint_share_of_year,
    DENSE_RANK() OVER (PARTITION BY received_year ORDER BY complaint_volume DESC)
        AS state_volume_rank_in_year
FROM state_year
ORDER BY received_year, complaint_volume DESC;

-- 10. Data-quality and mart reconciliation. Every row should pass before a dashboard refresh.
SELECT
    check_name,
    expected_value,
    actual_value,
    difference_value,
    status
FROM mart_data_quality_reconciliation
ORDER BY check_name;
