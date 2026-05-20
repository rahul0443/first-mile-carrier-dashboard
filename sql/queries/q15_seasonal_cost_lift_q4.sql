-- Query: q15_seasonal_cost_lift_q4
-- Business question: How much does Q4 peak season lift costs vs rest of year?
-- Returns: Q4 vs non-Q4 cost comparison across metrics.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q15_seasonal_cost_lift_q4.sql
-- Techniques: CASE, conditional aggregation, paired comparison

SELECT
    CASE WHEN d.month IN (10, 11, 12) THEN 'Q4 (Peak)' ELSE 'Non-Q4' END AS period,
    COUNT(*) AS shipment_count,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS avg_cpm,
    ROUND(AVG(f.linehaul_cost_usd), 2) AS avg_linehaul,
    ROUND(AVG(f.accessorial_cost_usd), 2) AS avg_accessorial,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct
FROM fact_shipment f
JOIN dim_date d ON f.shipment_date_key = d.date_key
GROUP BY period
ORDER BY period;
