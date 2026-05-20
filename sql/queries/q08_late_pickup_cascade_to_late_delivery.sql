-- Query: q08_late_pickup_cascade_to_late_delivery
-- Business question: How strongly do late pickups cascade into late deliveries?
-- Returns: Correlation between late pickup and late delivery rates.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q08_late_pickup_cascade_to_late_delivery.sql
-- Techniques: CASE, conditional aggregation, correlation analysis

SELECT
    'Late pickup -> Late delivery cascade' AS analysis,
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN NOT f.on_time_pickup AND NOT f.on_time_delivery THEN 1 ELSE 0 END) AS late_pickup_late_delivery,
    SUM(CASE WHEN NOT f.on_time_pickup AND f.on_time_delivery THEN 1 ELSE 0 END) AS late_pickup_ontime_delivery,
    SUM(CASE WHEN f.on_time_pickup AND NOT f.on_time_delivery THEN 1 ELSE 0 END) AS ontime_pickup_late_delivery,
    SUM(CASE WHEN f.on_time_pickup AND f.on_time_delivery THEN 1 ELSE 0 END) AS ontime_pickup_ontime_delivery,
    ROUND(
        SUM(CASE WHEN NOT f.on_time_pickup AND NOT f.on_time_delivery THEN 1.0 ELSE 0.0 END) /
        NULLIF(SUM(CASE WHEN NOT f.on_time_pickup THEN 1 ELSE 0 END), 0) * 100, 1
    ) AS pct_late_pickup_leads_to_late_delivery,
    ROUND(
        SUM(CASE WHEN f.on_time_pickup AND NOT f.on_time_delivery THEN 1.0 ELSE 0.0 END) /
        NULLIF(SUM(CASE WHEN f.on_time_pickup THEN 1 ELSE 0 END), 0) * 100, 1
    ) AS pct_ontime_pickup_still_late_delivery
FROM fact_shipment f
WHERE f.pickup_actual_ts IS NOT NULL;
