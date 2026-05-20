-- Query: q18_long_haul_vs_short_haul_economics
-- Business question: How do short-haul and long-haul lanes compare on economics?
-- Returns: Side-by-side comparison of short vs mid vs long haul lanes.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q18_long_haul_vs_short_haul_economics.sql
-- Techniques: JOIN, GROUP BY, CASE

SELECT
    l.lane_type,
    COUNT(*) AS shipment_count,
    ROUND(AVG(l.distance_miles), 0) AS avg_distance,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS avg_cpm,
    ROUND(AVG(f.accessorial_cost_usd / NULLIF(f.total_cost_usd, 0)) * 100, 1) AS accessorial_share_pct,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    ROUND(AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) * 100, 2) AS defect_rate_pct,
    ROUND(AVG(f.trailer_utilization_pct) * 100, 1) AS avg_utilization_pct
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.lane_type
ORDER BY avg_distance;
