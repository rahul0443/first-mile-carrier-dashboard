-- Query: q13_top20_shippers_costtoserve
-- Business question: What is the cost-to-serve for the top 20 shippers?
-- Returns: Top 20 shippers ranked by total spend with cost-to-serve metrics.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q13_top20_shippers_costtoserve.sql
-- Techniques: JOIN, GROUP BY, ORDER BY, LIMIT

SELECT
    s.shipper_name,
    s.vendor_type,
    s.ship_volume_tier,
    s.industry_segment,
    COUNT(*) AS shipment_count,
    ROUND(SUM(f.total_cost_usd), 2) AS total_cost,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)), 2) AS avg_cpm,
    ROUND(AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) * 100, 1) AS otd_pct,
    ROUND(AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) * 100, 2) AS defect_rate_pct
FROM fact_shipment f
JOIN dim_shipper s ON f.shipper_id = s.shipper_id
GROUP BY s.shipper_name, s.vendor_type, s.ship_volume_tier, s.industry_segment
ORDER BY total_cost DESC
LIMIT 20;
