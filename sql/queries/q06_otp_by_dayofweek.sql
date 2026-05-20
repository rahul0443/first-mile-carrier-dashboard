-- Query: q06_otp_by_dayofweek
-- Business question: Do certain days of the week have systematically worse OTP?
-- Returns: OTP by day of week to identify operational patterns.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q06_otp_by_dayofweek.sql
-- Techniques: JOIN, GROUP BY, CASE expression for day names

SELECT
    d.day_of_week,
    CASE d.day_of_week
        WHEN 0 THEN 'Monday'
        WHEN 1 THEN 'Tuesday'
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday'
        WHEN 4 THEN 'Friday'
        WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END AS day_name,
    COUNT(*) AS shipment_count,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    ROUND(AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) * 100, 2) AS defect_rate_pct,
    ROUND(AVG(f.dwell_minutes) FILTER (WHERE f.dwell_minutes > 0), 1) AS avg_dwell_min
FROM fact_shipment f
JOIN dim_date d ON f.shipment_date_key = d.date_key
GROUP BY d.day_of_week
ORDER BY d.day_of_week;
