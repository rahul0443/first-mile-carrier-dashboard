-- Query: q26_inbound_node_load_balance
-- Business question: Is inbound volume balanced across FCs or lopsided?
-- Returns: Volume and KPIs per inbound node (FC).
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q26_inbound_node_load_balance.sql
-- Techniques: JOIN, GROUP BY, comparison to network average

SELECT
    l.dest_fc_id,
    l.dest_city || ', ' || l.dest_state AS fc_location,
    COUNT(*) AS shipment_count,
    ROUND(COUNT(*)::DOUBLE / SUM(COUNT(*)) OVER () * 100, 1) AS volume_share_pct,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    ROUND(AVG(f.dwell_minutes) FILTER (WHERE f.dwell_minutes > 0), 1) AS avg_dwell,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.dest_fc_id, l.dest_city, l.dest_state
ORDER BY shipment_count DESC;
