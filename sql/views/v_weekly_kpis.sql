-- View: v_weekly_kpis
-- Weekly KPI time series for trend analysis and forecasting.

CREATE OR REPLACE VIEW v_weekly_kpis AS
SELECT
    d.year,
    d.week_of_year,
    MIN(d.date) AS week_start,
    COUNT(*) AS shipment_count,
    AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp_rate,
    AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) AS otd_rate,
    AVG(CASE WHEN f.dwell_minutes > 0 THEN f.dwell_minutes ELSE NULL END) AS avg_dwell,
    AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) AS defect_rate,
    AVG(f.trailer_utilization_pct) AS avg_utilization,
    AVG(f.total_cost_usd) AS avg_cost_per_shipment,
    AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS avg_cost_per_mile,
    SUM(f.total_cost_usd) AS total_cost
FROM fact_shipment f
JOIN dim_date d ON f.shipment_date_key = d.date_key
GROUP BY d.year, d.week_of_year
ORDER BY d.year, d.week_of_year;
