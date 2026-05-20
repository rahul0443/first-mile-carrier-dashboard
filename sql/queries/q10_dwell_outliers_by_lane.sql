-- Query: q10_dwell_outliers_by_lane
-- Business question: Which lanes have the most extreme dwell time outliers?
-- Returns: Lanes with dwell P99 > 180 minutes, indicating chronic detention.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q10_dwell_outliers_by_lane.sql
-- Techniques: PERCENTILE_CONT, HAVING, JOIN

SELECT
    l.lane_id,
    l.origin_city || ', ' || l.origin_state || ' -> ' || l.dest_fc_id AS lane,
    l.lane_type,
    COUNT(*) AS shipment_count,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY f.dwell_minutes)
          FILTER (WHERE f.dwell_minutes > 0), 1) AS dwell_p50,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY f.dwell_minutes)
          FILTER (WHERE f.dwell_minutes > 0), 1) AS dwell_p90,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY f.dwell_minutes)
          FILTER (WHERE f.dwell_minutes > 0), 1) AS dwell_p99
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.lane_id, l.origin_city, l.origin_state, l.dest_fc_id, l.lane_type
HAVING PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY f.dwell_minutes)
       FILTER (WHERE f.dwell_minutes > 0) > 180
ORDER BY dwell_p99 DESC;
