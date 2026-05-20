-- View: v_anomaly_flags
-- Aggregated anomaly indicators for the last 14 days.

CREATE OR REPLACE VIEW v_anomaly_flags AS
WITH recent AS (
    SELECT
        f.carrier_id,
        f.lane_id,
        d.date,
        d.week_of_year,
        AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS daily_otp,
        AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS daily_cpm,
        COUNT(*) AS daily_volume
    FROM fact_shipment f
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    WHERE d.date >= CURRENT_DATE - INTERVAL '14 days'
    GROUP BY f.carrier_id, f.lane_id, d.date, d.week_of_year
)
SELECT
    r.carrier_id,
    c.carrier_name,
    c.carrier_tier,
    r.lane_id,
    l.origin_city || ' -> ' || l.dest_fc_id AS lane_label,
    r.date,
    r.daily_otp,
    r.daily_cpm,
    r.daily_volume
FROM recent r
JOIN dim_carrier c ON r.carrier_id = c.carrier_id
JOIN dim_lane l ON r.lane_id = l.lane_id
ORDER BY r.date DESC, r.daily_otp ASC;
