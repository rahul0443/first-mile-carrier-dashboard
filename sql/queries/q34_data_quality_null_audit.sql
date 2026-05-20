-- Query: q34_data_quality_null_audit
-- Business question: What is the completeness profile of the fact table?
-- Returns: NULL counts and percentages for each column.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q34_data_quality_null_audit.sql
-- Techniques: Conditional aggregation, UNION ALL

SELECT 'pickup_actual_ts' AS column_name,
       COUNT(*) FILTER (WHERE pickup_actual_ts IS NULL) AS null_count,
       COUNT(*) AS total_rows,
       ROUND(COUNT(*) FILTER (WHERE pickup_actual_ts IS NULL)::DOUBLE / COUNT(*) * 100, 3) AS null_pct
FROM fact_shipment
UNION ALL
SELECT 'delivery_actual_ts',
       COUNT(*) FILTER (WHERE delivery_actual_ts IS NULL),
       COUNT(*),
       ROUND(COUNT(*) FILTER (WHERE delivery_actual_ts IS NULL)::DOUBLE / COUNT(*) * 100, 3)
FROM fact_shipment
UNION ALL
SELECT 'defect_reason',
       COUNT(*) FILTER (WHERE defect_reason IS NULL),
       COUNT(*),
       ROUND(COUNT(*) FILTER (WHERE defect_reason IS NULL)::DOUBLE / COUNT(*) * 100, 3)
FROM fact_shipment
ORDER BY null_pct DESC;
