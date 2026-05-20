-- Query: q02_otp_by_carrier_tier
-- Business question: How does OTP vary across carrier tiers, and who are the
--   top/bottom performers within each tier?
-- Returns: Carriers ranked by OTP within their tier using window functions.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q02_otp_by_carrier_tier.sql
-- Techniques: Window function (RANK), JOIN, GROUP BY

SELECT
    c.carrier_tier,
    c.carrier_name,
    COUNT(*) AS shipment_count,
    ROUND(AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) * 100, 1) AS otp_pct,
    c.target_otp_pct * 100 AS target_otp_pct,
    RANK() OVER (
        PARTITION BY c.carrier_tier
        ORDER BY AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) DESC
    ) AS rank_within_tier
FROM fact_shipment f
JOIN dim_carrier c ON f.carrier_id = c.carrier_id
GROUP BY c.carrier_tier, c.carrier_name, c.target_otp_pct
ORDER BY c.carrier_tier, rank_within_tier;
