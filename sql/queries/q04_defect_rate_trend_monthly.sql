-- Query: q04_defect_rate_trend_monthly
-- Business question: Is defect rate improving or worsening month-over-month?
-- Returns: Monthly defect rate trend with defect count and total shipments.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q04_defect_rate_trend_monthly.sql
-- Techniques: JOIN, GROUP BY, DATE functions

SELECT
    d.year,
    d.month,
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN f.defect_flag THEN 1 ELSE 0 END) AS defect_count,
    ROUND(AVG(CASE WHEN f.defect_flag THEN 1.0 ELSE 0.0 END) * 100, 2) AS defect_rate_pct
FROM fact_shipment f
JOIN dim_date d ON f.shipment_date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
