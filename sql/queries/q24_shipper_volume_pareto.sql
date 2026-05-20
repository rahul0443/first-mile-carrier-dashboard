-- Query: q24_shipper_volume_pareto
-- Business question: What is the shipper volume distribution (Pareto curve)?
-- Returns: Shipper volumes with cumulative running total (for 80/20 analysis).
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q24_shipper_volume_pareto.sql
-- Techniques: Window function (running SUM), CTE, ROW_NUMBER

WITH shipper_vols AS (
    SELECT
        s.shipper_name,
        s.ship_volume_tier,
        COUNT(*) AS shipment_count,
        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rank
    FROM fact_shipment f
    JOIN dim_shipper s ON f.shipper_id = s.shipper_id
    GROUP BY s.shipper_name, s.ship_volume_tier
)
SELECT
    rank,
    shipper_name,
    ship_volume_tier,
    shipment_count,
    ROUND(shipment_count::DOUBLE / SUM(shipment_count) OVER () * 100, 2) AS pct_of_total,
    ROUND(SUM(shipment_count) OVER (ORDER BY rank)::DOUBLE /
          SUM(shipment_count) OVER () * 100, 1) AS cumulative_pct
FROM shipper_vols
ORDER BY rank
LIMIT 50;
