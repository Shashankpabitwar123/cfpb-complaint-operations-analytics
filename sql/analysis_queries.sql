-- Monthly volume
SELECT month_start, year, COUNT(DISTINCT complaint_id) AS complaint_count
FROM complaints
GROUP BY month_start, year
ORDER BY month_start;

-- Product workload
SELECT product, COUNT(DISTINCT complaint_id) AS complaint_count
FROM complaints
GROUP BY product
ORDER BY complaint_count DESC;

-- Response coverage and timeliness; denominators are explicit.
SELECT year,
       COUNT(DISTINCT complaint_id) AS complaint_count,
       SUM(has_company_response) AS known_public_response_count,
       100.0 * SUM(has_company_response) / COUNT(DISTINCT complaint_id) AS response_coverage_pct,
       SUM(CASE WHEN timely_response_flag = 'Yes' THEN 1 ELSE 0 END) AS timely_yes_count,
       SUM(CASE WHEN timely_response_flag IN ('Yes','No') THEN 1 ELSE 0 END) AS timely_known_count,
       100.0 * SUM(CASE WHEN timely_response_flag = 'Yes' THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN timely_response_flag IN ('Yes','No') THEN 1 ELSE 0 END), 0) AS timely_response_rate_pct
FROM complaints
GROUP BY year
ORDER BY year;

-- Submission channel mix
SELECT year, submitted_via, COUNT(DISTINCT complaint_id) AS complaint_count
FROM complaints
GROUP BY year, submitted_via
ORDER BY year, complaint_count DESC;
