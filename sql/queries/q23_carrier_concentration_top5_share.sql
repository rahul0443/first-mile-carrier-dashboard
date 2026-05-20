-- Query: q23_carrier_concentration_top5_share
-- Business question: How concentrated is carrier usage? What share do top 5 have?
-- Returns: Top 5 carriers by volume with cumulative share.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q23_carrier_concentration_top5_share.sql
-- Techniques: Window function (running SUM), CTE

WITH carrier_volumes AS (
    SELECT
        c.carrier_name,
        c.carrier_tier,
        COUNT(*) AS shipment_count,
        COUNT(*)::DOUBLE / SUM(COUNT(*)) OVER () AS volume_share
    FROM fact_shipment f
    JOIN dim_carrier c ON f.carrier_id = c.carrier_id
    GROUP BY c.carrier_name, c.carrier_tier
)
SELECT
    carrier_name,
    carrier_tier,
    shipment_count,
    ROUND(volume_share * 100, 1) AS volume_share_pct,
    ROUND(SUM(volume_share) OVER (ORDER BY shipment_count DESC) * 100, 1) AS cumulative_share_pct
FROM carrier_volumes
ORDER BY shipment_count DESC
LIMIT 10;
