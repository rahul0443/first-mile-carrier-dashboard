-- Query: q35_negative_dwell_audit
-- Business question: How many shipments have negative dwell (early arrivals)?
-- Returns: Count, percentage, and distribution of negative dwell records.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q35_negative_dwell_audit.sql
-- Techniques: Conditional aggregation, FILTER, PERCENTILE_CONT

SELECT
    COUNT(*) FILTER (WHERE dwell_minutes < 0) AS negative_dwell_count,
    COUNT(*) AS total_shipments,
    ROUND(COUNT(*) FILTER (WHERE dwell_minutes < 0)::DOUBLE / COUNT(*) * 100, 3) AS negative_dwell_pct,
    ROUND(MIN(dwell_minutes) FILTER (WHERE dwell_minutes < 0), 1) AS most_negative_minutes,
    ROUND(AVG(dwell_minutes) FILTER (WHERE dwell_minutes < 0), 1) AS avg_negative_minutes,
    'Early arrivals before appointment window. Clipped or filtered in analysis.' AS handling_note
FROM fact_shipment;
