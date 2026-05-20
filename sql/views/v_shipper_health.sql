-- View: v_shipper_health
-- Composite Shipper Health Score (SHS) from 0-100.
-- Weights: Service 30%, Cost 25%, Growth 20%, Reliability 15%, Tenure 10%.

CREATE OR REPLACE VIEW v_shipper_health AS
WITH shipper_metrics AS (
    SELECT
        s.shipper_id,
        s.shipper_name,
        s.vendor_type,
        s.ship_volume_tier,
        s.industry_segment,
        s.onboarding_date,
        COUNT(*) AS total_shipments,
        AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) AS otd_rate,
        AVG(CASE WHEN NOT f.defect_flag THEN 1.0 ELSE 0.0 END) AS defect_free_rate,
        AVG(f.total_cost_usd) AS avg_cost_per_shipment,
        STDDEV(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp_stddev
    FROM fact_shipment f
    JOIN dim_shipper s ON f.shipper_id = s.shipper_id
    GROUP BY s.shipper_id, s.shipper_name, s.vendor_type,
             s.ship_volume_tier, s.industry_segment, s.onboarding_date
),
growth AS (
    SELECT
        f.shipper_id,
        COUNT(CASE WHEN d.date >= CURRENT_DATE - INTERVAL '90 days' THEN 1 END) AS vol_last_90d,
        COUNT(CASE WHEN d.date >= CURRENT_DATE - INTERVAL '180 days'
                    AND d.date < CURRENT_DATE - INTERVAL '90 days' THEN 1 END) AS vol_prior_90d
    FROM fact_shipment f
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    GROUP BY f.shipper_id
),
tier_benchmarks AS (
    SELECT
        s.ship_volume_tier,
        AVG(f.total_cost_usd) AS tier_avg_cost
    FROM fact_shipment f
    JOIN dim_shipper s ON f.shipper_id = s.shipper_id
    GROUP BY s.ship_volume_tier
)
SELECT
    m.shipper_id,
    m.shipper_name,
    m.vendor_type,
    m.ship_volume_tier,
    m.industry_segment,
    m.total_shipments,
    m.otd_rate,
    m.defect_free_rate,
    m.avg_cost_per_shipment,
    g.vol_last_90d,
    g.vol_prior_90d,
    CASE WHEN g.vol_prior_90d > 0
         THEN (g.vol_last_90d - g.vol_prior_90d)::DOUBLE / g.vol_prior_90d
         ELSE 0 END AS growth_rate,
    -- Service score (0-100): weighted average of OTD and defect-free rate
    (m.otd_rate * 0.6 + m.defect_free_rate * 0.4) * 100 AS service_score,
    -- Cost score (0-100): lower cost-to-serve vs benchmark is better
    LEAST(100, GREATEST(0,
        (1 - (m.avg_cost_per_shipment - tb.tier_avg_cost) / NULLIF(tb.tier_avg_cost, 0)) * 100
    )) AS cost_score,
    -- Growth score (0-100): positive growth is better, capped
    LEAST(100, GREATEST(0,
        50 + CASE WHEN g.vol_prior_90d > 0
             THEN ((g.vol_last_90d - g.vol_prior_90d)::DOUBLE / g.vol_prior_90d) * 100
             ELSE 0 END
    )) AS growth_score,
    -- Reliability score (0-100): lower variance is better
    LEAST(100, GREATEST(0, (1 - m.otp_stddev * 2) * 100)) AS reliability_score,
    -- Tenure score (0-100): months since onboarding, capped at 24
    LEAST(100, (DATEDIFF('month', m.onboarding_date, CURRENT_DATE)::DOUBLE / 24) * 100) AS tenure_score,
    -- Composite SHS
    (
        0.30 * (m.otd_rate * 0.6 + m.defect_free_rate * 0.4) * 100
      + 0.25 * LEAST(100, GREATEST(0,
            (1 - (m.avg_cost_per_shipment - tb.tier_avg_cost) / NULLIF(tb.tier_avg_cost, 0)) * 100))
      + 0.20 * LEAST(100, GREATEST(0,
            50 + CASE WHEN g.vol_prior_90d > 0
                 THEN ((g.vol_last_90d - g.vol_prior_90d)::DOUBLE / g.vol_prior_90d) * 100
                 ELSE 0 END))
      + 0.15 * LEAST(100, GREATEST(0, (1 - m.otp_stddev * 2) * 100))
      + 0.10 * LEAST(100, (DATEDIFF('month', m.onboarding_date, CURRENT_DATE)::DOUBLE / 24) * 100)
    ) AS shipper_health_score
FROM shipper_metrics m
JOIN growth g ON m.shipper_id = g.shipper_id
JOIN tier_benchmarks tb ON m.ship_volume_tier = tb.ship_volume_tier
ORDER BY shipper_health_score DESC;
