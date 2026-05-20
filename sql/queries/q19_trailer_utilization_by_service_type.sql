-- Query: q19_trailer_utilization_by_service_type
-- Business question: How does trailer utilization vary by service type?
-- Returns: Utilization distribution statistics by mode.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q19_trailer_utilization_by_service_type.sql
-- Techniques: JOIN, GROUP BY, PERCENTILE_CONT

SELECT
    st.service_name,
    COUNT(*) AS shipment_count,
    ROUND(AVG(f.trailer_utilization_pct) * 100, 1) AS avg_utilization_pct,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY f.trailer_utilization_pct) * 100, 1) AS util_p25,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY f.trailer_utilization_pct) * 100, 1) AS util_p50,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY f.trailer_utilization_pct) * 100, 1) AS util_p75,
    ROUND(SUM(CASE WHEN f.trailer_utilization_pct < 0.50 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 1) AS pct_under_50
FROM fact_shipment f
JOIN dim_service_type st ON f.service_type_id = st.service_type_id
GROUP BY st.service_name
ORDER BY avg_utilization_pct;
