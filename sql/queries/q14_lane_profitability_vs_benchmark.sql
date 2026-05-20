-- Query: q14_lane_profitability_vs_benchmark
-- Business question: Which lanes are profitable vs unprofitable against benchmark CPM?
-- Returns: Lane Profitability Index: (benchmark - observed) / benchmark.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q14_lane_profitability_vs_benchmark.sql
-- Techniques: JOIN, GROUP BY, computed columns, CASE

SELECT
    l.lane_id,
    l.origin_city || ' -> ' || l.dest_fc_id AS lane,
    l.lane_type,
    l.distance_miles,
    COUNT(*) AS shipment_count,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS observed_cpm,
    2.43 AS benchmark_cpm,
    ROUND((2.43 - AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0))) / 2.43 * 100, 1) AS profitability_index_pct,
    CASE
        WHEN AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) > 2.43 THEN 'Above benchmark'
        ELSE 'Below benchmark'
    END AS cost_status
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.lane_id, l.origin_city, l.dest_fc_id, l.lane_type, l.distance_miles
HAVING COUNT(*) >= 100
ORDER BY profitability_index_pct ASC;
