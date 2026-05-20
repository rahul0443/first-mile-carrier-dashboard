-- View: v_shipper_costtoserve
-- Per-shipper cost-to-serve analysis for pricing recommendations.

CREATE OR REPLACE VIEW v_shipper_costtoserve AS
SELECT
    s.shipper_id,
    s.shipper_name,
    s.vendor_type,
    s.ship_volume_tier,
    COUNT(*) AS shipment_count,
    SUM(f.total_cost_usd) AS total_cost,
    AVG(f.total_cost_usd) AS avg_cost_per_shipment,
    AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS avg_cost_per_mile,
    AVG(f.total_cost_usd / NULLIF(f.pallet_count, 0)) AS avg_cost_per_pallet,
    AVG(f.accessorial_cost_usd / NULLIF(f.total_cost_usd, 0)) AS accessorial_share,
    AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) AS otd_rate,
    AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) AS defect_rate
FROM fact_shipment f
JOIN dim_shipper s ON f.shipper_id = s.shipper_id
GROUP BY s.shipper_id, s.shipper_name, s.vendor_type, s.ship_volume_tier
ORDER BY total_cost DESC;
