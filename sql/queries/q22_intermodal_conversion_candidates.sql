-- Query: q22_intermodal_conversion_candidates
-- Business question: Which long-haul FTL lanes could save money via intermodal?
-- Returns: FTL lanes > 1500 miles with volume sufficient for intermodal.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q22_intermodal_conversion_candidates.sql
-- Techniques: JOIN, GROUP BY, HAVING, subquery

SELECT
    l.lane_id,
    l.origin_city || ' -> ' || l.dest_fc_id AS lane,
    l.distance_miles,
    COUNT(*) AS ftl_volume,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS current_cpm,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) * 0.80, 2) AS est_intermodal_cpm,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) * 0.20 * AVG(f.distance_miles) * COUNT(*), 0) AS est_annual_savings,
    'Evaluate intermodal conversion' AS recommendation
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
JOIN dim_service_type st ON f.service_type_id = st.service_type_id
WHERE st.service_name = 'FTL' AND l.distance_miles > 1500
GROUP BY l.lane_id, l.origin_city, l.dest_fc_id, l.distance_miles
HAVING COUNT(*) >= 100
ORDER BY est_annual_savings DESC
LIMIT 15;
