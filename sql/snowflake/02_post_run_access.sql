-- Run after dbt has created analytics tables if a separate reader role is needed.
-- Replace TABLEAU_READER with an approved reader role; do not use this script on Tableau Public.

-- GRANT USAGE ON WAREHOUSE CFPB_PORTFOLIO_WH TO ROLE TABLEAU_READER;
-- GRANT USAGE ON DATABASE CFPB_ANALYTICS TO ROLE TABLEAU_READER;
-- GRANT USAGE ON SCHEMA CFPB_ANALYTICS.ANALYTICS TO ROLE TABLEAU_READER;
-- GRANT SELECT ON ALL TABLES IN SCHEMA CFPB_ANALYTICS.ANALYTICS TO ROLE TABLEAU_READER;
-- GRANT SELECT ON FUTURE TABLES IN SCHEMA CFPB_ANALYTICS.ANALYTICS TO ROLE TABLEAU_READER;

-- Tableau Public cannot retain a live Snowflake connection. Export Tableau-ready
-- mart extracts with scripts/export_tableau_marts.py and publish the extract snapshot.
