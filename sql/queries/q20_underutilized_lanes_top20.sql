-- Query: q20_underutilized_lanes_top20
-- Business question: Which lanes have the lowest trailer utilization (waste)?
-- Returns: Bottom 20 lanes by average utilization.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q20_underutilized_lanes_top20.sql
-- Techniques: JOIN, GROUP BY, HAVING, ORDER BY

SELECT
    l.lane_id,
    l.origin_city || ' -> ' || l.dest_fc_id AS lane,
    l.lane_type,
    COUNT(*) AS shipment_count,
    ROUND(AVG(f.trailer_utilization_pct) * 100, 1) AS avg_utilization_pct,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS avg_cpm
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.lane_id, l.origin_city, l.dest_fc_id, l.lane_type
HAVING COUNT(*) >= 50
ORDER BY avg_utilization_pct ASC
LIMIT 20;
