-- Query: q25_origin_state_volume_distribution
-- Business question: Which origin states generate the most inbound volume?
-- Returns: Volume and cost metrics by origin state.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q25_origin_state_volume_distribution.sql
-- Techniques: JOIN, GROUP BY, ORDER BY

SELECT
    l.origin_state,
    COUNT(DISTINCT l.lane_id) AS lane_count,
    COUNT(*) AS shipment_count,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment,
    ROUND(SUM(f.total_cost_usd), 0) AS total_cost
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.origin_state
ORDER BY shipment_count DESC;
