-- Query: q05_carrier_lane_otp_matrix
-- Business question: Which carrier-lane combinations have the best/worst OTP?
-- Returns: Pivoted view of OTP by carrier and lane for heatmap visualization.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q05_carrier_lane_otp_matrix.sql
-- Techniques: JOIN, GROUP BY, HAVING (volume filter)

SELECT
    c.carrier_name,
    c.carrier_tier,
    l.origin_city || '->' || l.dest_fc_id AS lane,
    COUNT(*) AS shipment_count,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS cost_per_mile
FROM fact_shipment f
JOIN dim_carrier c ON f.carrier_id = c.carrier_id
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY c.carrier_name, c.carrier_tier, lane
HAVING COUNT(*) >= 50
ORDER BY otp_pct ASC
LIMIT 50;
