-- Query: q03_dwell_p50_p90_p99_by_carrier
-- Business question: Which carriers are creating the worst detention exposure?
-- Returns: One row per carrier with dwell percentiles, sorted P90 desc.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q03_dwell_p50_p90_p99_by_carrier.sql
-- Techniques: PERCENTILE_CONT, GROUP BY, ORDER BY, FILTER

SELECT
    c.carrier_name,
    c.carrier_tier,
    COUNT(*) AS shipment_count,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY f.dwell_minutes)
          FILTER (WHERE f.dwell_minutes > 0), 1) AS dwell_p50,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY f.dwell_minutes)
          FILTER (WHERE f.dwell_minutes > 0), 1) AS dwell_p90,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY f.dwell_minutes)
          FILTER (WHERE f.dwell_minutes > 0), 1) AS dwell_p99
FROM fact_shipment f
JOIN dim_carrier c ON f.carrier_id = c.carrier_id
GROUP BY c.carrier_name, c.carrier_tier
ORDER BY dwell_p90 DESC;
