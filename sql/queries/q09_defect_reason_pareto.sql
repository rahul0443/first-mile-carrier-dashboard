-- Query: q09_defect_reason_pareto
-- Business question: Which defect reasons account for the majority of defects?
-- Returns: Defect reasons ranked by frequency with cumulative percentage (Pareto).
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q09_defect_reason_pareto.sql
-- Techniques: Window function (SUM OVER for running total), CTE

WITH defects AS (
    SELECT
        defect_reason,
        COUNT(*) AS defect_count
    FROM fact_shipment
    WHERE defect_flag = TRUE AND defect_reason IS NOT NULL
    GROUP BY defect_reason
)
SELECT
    defect_reason,
    defect_count,
    ROUND(defect_count * 100.0 / SUM(defect_count) OVER (), 1) AS pct_of_total,
    ROUND(SUM(defect_count) OVER (ORDER BY defect_count DESC) * 100.0 /
          SUM(defect_count) OVER (), 1) AS cumulative_pct
FROM defects
ORDER BY defect_count DESC;
