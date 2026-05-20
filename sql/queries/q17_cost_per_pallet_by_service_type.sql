-- Query: q17_cost_per_pallet_by_service_type
-- Business question: What is the unit economics per pallet by service type?
-- Returns: Cost per pallet by service type.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q17_cost_per_pallet_by_service_type.sql
-- Techniques: JOIN, GROUP BY, aggregate functions

SELECT
    st.service_name,
    COUNT(*) AS shipment_count,
    ROUND(AVG(f.total_cost_usd / NULLIF(f.pallet_count, 0)), 2) AS avg_cost_per_pallet,
    ROUND(AVG(f.total_cost_usd), 2) AS avg_cost_per_shipment,
    ROUND(AVG(f.pallet_count), 1) AS avg_pallets_per_shipment,
    ROUND(AVG(f.trailer_utilization_pct) * 100, 1) AS avg_utilization_pct
FROM fact_shipment f
JOIN dim_service_type st ON f.service_type_id = st.service_type_id
GROUP BY st.service_name
ORDER BY avg_cost_per_pallet;
