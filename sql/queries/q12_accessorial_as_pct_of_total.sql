-- Query: q12_accessorial_as_pct_of_total
-- Business question: What share of total cost comes from accessorials by carrier?
-- Returns: Accessorial share ranking by carrier.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q12_accessorial_as_pct_of_total.sql
-- Techniques: JOIN, GROUP BY, conditional aggregation

SELECT
    c.carrier_name,
    c.carrier_tier,
    COUNT(*) AS shipment_count,
    ROUND(SUM(f.accessorial_cost_usd), 2) AS total_accessorial,
    ROUND(SUM(f.total_cost_usd), 2) AS total_cost,
    ROUND(SUM(f.accessorial_cost_usd) / NULLIF(SUM(f.total_cost_usd), 0) * 100, 1) AS accessorial_pct
FROM fact_shipment f
JOIN dim_carrier c ON f.carrier_id = c.carrier_id
GROUP BY c.carrier_name, c.carrier_tier
ORDER BY accessorial_pct DESC;
