-- View: v_lane_performance
-- Lane-level performance metrics for heatmap and drill-down.

CREATE OR REPLACE VIEW v_lane_performance AS
SELECT
    l.lane_id,
    l.origin_city,
    l.origin_state,
    l.dest_fc_id,
    l.distance_miles,
    l.lane_type,
    COUNT(*) AS shipment_count,
    AVG(CASE WHEN f.on_time_pickup THEN 1.0 ELSE 0.0 END) AS otp_rate,
    AVG(CASE WHEN f.on_time_delivery THEN 1.0 ELSE 0.0 END) AS otd_rate,
    AVG(CASE WHEN f.dwell_minutes > 0 THEN f.dwell_minutes ELSE NULL END) AS avg_dwell_minutes,
    AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) AS defect_rate,
    AVG(f.trailer_utilization_pct) AS avg_utilization,
    AVG(f.total_cost_usd) AS avg_cost_per_shipment,
    AVG(f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS avg_cost_per_mile,
    SUM(f.total_cost_usd) AS total_cost
FROM fact_shipment f
JOIN dim_lane l ON f.lane_id = l.lane_id
GROUP BY l.lane_id, l.origin_city, l.origin_state, l.dest_fc_id,
         l.distance_miles, l.lane_type
ORDER BY shipment_count DESC;
