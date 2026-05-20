-- Query: q27_otp_wow_pct_change
-- Business question: What is the week-over-week OTP trend?
-- Returns: Weekly OTP with WoW change using LAG window function.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q27_otp_wow_pct_change.sql
-- Techniques: CTE, LAG window function

WITH weekly_otp AS (
    SELECT
        d.year,
        d.week_of_year,
        MIN(d.date) AS week_start,
        ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct
    FROM fact_shipment f
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    GROUP BY d.year, d.week_of_year
)
SELECT
    year,
    week_of_year,
    week_start,
    otp_pct,
    LAG(otp_pct) OVER (ORDER BY year, week_of_year) AS prev_week_otp,
    ROUND(otp_pct - LAG(otp_pct) OVER (ORDER BY year, week_of_year), 1) AS wow_change_pp
FROM weekly_otp
ORDER BY year, week_of_year;
