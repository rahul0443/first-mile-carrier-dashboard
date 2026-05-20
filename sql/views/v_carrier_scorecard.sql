-- View: v_carrier_scorecard
-- Carrier-level KPI scorecard for ranking and benchmarking.

CREATE OR REPLACE VIEW v_carrier_scorecard AS
SELECT
    c.carrier_id,
    c.carrier_name,
    c.carrier_tier,
    c.equipment_type,
    c.contract_type,
    c.target_otp_pct,
    COUNT(*) AS shipment_count,
    AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp_rate,
    AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) AS otd_rate,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY CASE WHEN f.dwell_minutes > 0 THEN f.dwell_minutes END) AS dwell_p50,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY CASE WHEN f.dwell_minutes > 0 THEN f.dwell_minutes END) AS dwell_p90,
    AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) AS defect_rate,
    AVG(f.trailer_utilization_pct) AS avg_utilization,
    AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS avg_cost_per_mile,
    AVG(f.total_cost_usd) AS avg_cost_per_shipment,
    SUM(f.total_cost_usd) AS total_cost
FROM fact_shipment f
JOIN dim_carrier c ON f.carrier_id = c.carrier_id
GROUP BY c.carrier_id, c.carrier_name, c.carrier_tier,
         c.equipment_type, c.contract_type, c.target_otp_pct
ORDER BY c.carrier_tier, otp_rate DESC;
