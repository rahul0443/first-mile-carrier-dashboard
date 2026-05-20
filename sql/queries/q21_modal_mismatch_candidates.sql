-- Query: q21_modal_mismatch_candidates
-- Business question: Which LTL shipments have characteristics suggesting they
--   should be FTL (high utilization, high weight)?
-- Returns: LTL shipments that look like FTL candidates.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q21_modal_mismatch_candidates.sql
-- Techniques: JOIN, GROUP BY, HAVING, conditional logic

SELECT
    l.lane_id,
    l.origin_city || ' -> ' || l.dest_fc_id AS lane,
    COUNT(*) AS ltl_shipment_count,
    ROUND(AVG(f.trailer_utilization_pct) * 100, 1) AS avg_utilization_pct,
    ROUND(AVG(f.weight_lbs), 0) AS avg_weight_lbs,
    ROUND(AVG(f.pallet_count), 1) AS avg_pallets,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_ltl,
    'Consider FTL conversion' AS recommendation
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
JOIN dim_service_type st ON f.service_type_id = st.service_type_id
WHERE st.service_name = 'LTL'
GROUP BY l.lane_id, l.origin_city, l.dest_fc_id
HAVING AVG(f.trailer_utilization_pct) > 0.70
   AND AVG(f.weight_lbs) > 30000
   AND COUNT(*) >= 20
ORDER BY avg_utilization_pct DESC;
