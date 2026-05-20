-- Query: q01_top10_lanes_by_volume
-- Business question: Which lanes carry the most shipment volume?
-- Returns: Top 10 lanes by shipment count with origin, destination, and OTP.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q01_top10_lanes_by_volume.sql
-- Techniques: JOIN, GROUP BY, ORDER BY, LIMIT

SELECT
    l.lane_id,
    l.origin_city || ', ' || l.origin_state AS origin,
    l.dest_fc_id AS destination,
    l.distance_miles,
    l.lane_type,
    COUNT(*) AS shipment_count,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.lane_id, l.origin_city, l.origin_state, l.dest_fc_id,
         l.distance_miles, l.lane_type
ORDER BY shipment_count DESC
LIMIT 10;
