-- Query: q16_accessorial_pareto_by_reason
-- Business question: Which accessorial reasons drive the most cost?
-- Returns: Accessorial breakdown by defect reason with Pareto analysis.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q16_accessorial_pareto_by_reason.sql
-- Techniques: Window function (running sum), CTE, GROUP BY

WITH by_reason AS (
    SELECT
        COALESCE(f.defect_reason, 'No defect (standard accessorial)') AS reason,
        COUNT(*) AS shipment_count,
        ROUND(SUM(f.accessorial_cost_usd), 2) AS total_accessorial,
        ROUND(AVG(f.accessorial_cost_usd), 2) AS avg_accessorial
    FROM fact_shipment f
    WHERE f.accessorial_cost_usd > 0
    GROUP BY reason
)
SELECT
    reason,
    shipment_count,
    total_accessorial,
    avg_accessorial,
    ROUND(total_accessorial / SUM(total_accessorial) OVER () * 100, 1) AS pct_of_total,
    ROUND(SUM(total_accessorial) OVER (ORDER BY total_accessorial DESC) /
          SUM(total_accessorial) OVER () * 100, 1) AS cumulative_pct
FROM by_reason
ORDER BY total_accessorial DESC;
