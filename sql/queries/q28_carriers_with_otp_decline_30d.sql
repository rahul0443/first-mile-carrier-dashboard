-- Query: q28_carriers_with_otp_decline_30d
-- Business question: Which carriers have seen OTP decline by >5pp in the last
--   4 weeks vs the prior 4 weeks?
-- Returns: Carriers with significant recent OTP deterioration.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q28_carriers_with_otp_decline_30d.sql
-- Techniques: CTE, conditional aggregation, HAVING

WITH periods AS (
    SELECT
        c.carrier_id,
        c.carrier_name,
        c.carrier_tier,
        AVG(CASE WHEN d.date >= CURRENT_DATE - INTERVAL '28 days'
             THEN CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END END) AS otp_last_4w,
        AVG(CASE WHEN d.date >= CURRENT_DATE - INTERVAL '56 days'
                  AND d.date < CURRENT_DATE - INTERVAL '28 days'
             THEN CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END END) AS otp_prior_4w
    FROM fact_shipment f
    JOIN dim_carrier c ON f.carrier_id = c.carrier_id
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    WHERE d.date >= CURRENT_DATE - INTERVAL '56 days'
    GROUP BY c.carrier_id, c.carrier_name, c.carrier_tier
)
SELECT
    carrier_name,
    carrier_tier,
    ROUND(otp_prior_4w * 100, 1) AS otp_prior_4w_pct,
    ROUND(otp_last_4w * 100, 1) AS otp_last_4w_pct,
    ROUND((otp_last_4w - otp_prior_4w) * 100, 1) AS change_pp
FROM periods
WHERE otp_prior_4w IS NOT NULL AND otp_last_4w IS NOT NULL
  AND (otp_last_4w - otp_prior_4w) < -0.05
ORDER BY change_pp ASC;
