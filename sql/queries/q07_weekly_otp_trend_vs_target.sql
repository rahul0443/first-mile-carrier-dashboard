-- Query: q07_weekly_otp_trend_vs_target
-- Business question: How does weekly OTP track against the network target,
--   and what is the rolling 4-week average?
-- Returns: Weekly OTP with rolling 4-week average and target comparison.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q07_weekly_otp_trend_vs_target.sql
-- Techniques: CTE, Window function (AVG OVER ROWS), JOIN

WITH weekly AS (
    SELECT
        d.year,
        d.week_of_year,
        MIN(d.date) AS week_start,
        COUNT(*) AS shipment_count,
        AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp_rate
    FROM fact_shipment f
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    GROUP BY d.year, d.week_of_year
)
SELECT
    year,
    week_of_year,
    week_start,
    shipment_count,
    ROUND(otp_rate * 100, 1) AS otp_pct,
    ROUND(AVG(otp_rate) OVER (
        ORDER BY year, week_of_year
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) * 100, 1) AS rolling_4w_avg_pct,
    90.0 AS network_target_pct
FROM weekly
ORDER BY year, week_of_year;
