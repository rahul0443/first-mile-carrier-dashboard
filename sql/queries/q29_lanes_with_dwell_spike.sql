-- Query: q29_lanes_with_dwell_spike
-- Business question: Which lanes have seen a dwell spike in the last 2 weeks?
-- Returns: Lanes where recent dwell P90 exceeds trailing average by >50%.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q29_lanes_with_dwell_spike.sql
-- Techniques: CTE, conditional aggregation, PERCENTILE_CONT

WITH baseline AS (
    SELECT
        l.lane_id,
        l.origin_city || ' -> ' || l.dest_fc_id AS lane,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY f.dwell_minutes)
            FILTER (WHERE f.dwell_minutes > 0) AS baseline_dwell_p90
    FROM fact_shipment f
    JOIN dim_lane l ON f.lane_id = l.lane_id
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    WHERE d.date < CURRENT_DATE - INTERVAL '14 days'
    GROUP BY l.lane_id, l.origin_city, l.dest_fc_id
),
recent AS (
    SELECT
        l.lane_id,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY f.dwell_minutes)
            FILTER (WHERE f.dwell_minutes > 0) AS recent_dwell_p90,
        COUNT(*) AS recent_volume
    FROM fact_shipment f
    JOIN dim_lane l ON f.lane_id = l.lane_id
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    WHERE d.date >= CURRENT_DATE - INTERVAL '14 days'
    GROUP BY l.lane_id
)
SELECT
    b.lane,
    b.baseline_dwell_p90,
    r.recent_dwell_p90,
    ROUND((r.recent_dwell_p90 - b.baseline_dwell_p90) / NULLIF(b.baseline_dwell_p90, 0) * 100, 1) AS pct_change,
    r.recent_volume
FROM baseline b
JOIN recent r ON b.lane_id = r.lane_id
WHERE r.recent_dwell_p90 > b.baseline_dwell_p90 * 1.5
  AND r.recent_volume >= 10
ORDER BY pct_change DESC;
