-- Query: q11_cost_per_mile_by_carrier_tier
-- Business question: What is the cost-per-mile by carrier tier?
-- Returns: Average CPM by tier with volume context.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q11_cost_per_mile_by_carrier_tier.sql
-- Techniques: JOIN, GROUP BY, aggregate functions

SELECT
    c.carrier_tier,
    COUNT(*) AS shipment_count,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS avg_cost_per_mile,
    ROUND(MIN(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS min_cpm,
    ROUND(MAX(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS max_cpm,
    ROUND(SUM(f.total_cost_usd), 2) AS total_spend
FROM fact_shipment f
JOIN dim_carrier c ON f.carrier_id = c.carrier_id
GROUP BY c.carrier_tier
ORDER BY avg_cost_per_mile;
