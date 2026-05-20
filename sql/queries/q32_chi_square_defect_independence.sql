-- Query: q32_chi_square_defect_independence
-- Business question: Is defect occurrence independent of carrier tier?
-- Returns: Chi-square test of independence between carrier tier and defect flag.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q32_chi_square_defect_independence.sql
-- Techniques: CTE, cross-tabulation, chi-square computation

-- Chi-square test: H0 = defect occurrence is independent of carrier tier
-- Compute observed frequencies, expected frequencies, then chi-square statistic.
-- Critical value at df=3, alpha=0.05 is 7.815.

WITH observed AS (
    SELECT
        c.carrier_tier,
        SUM(CASE WHEN f.defect_flag THEN 1 ELSE 0 END) AS defect_yes,
        SUM(CASE WHEN NOT f.defect_flag THEN 1 ELSE 0 END) AS defect_no,
        COUNT(*) AS row_total
    FROM fact_shipment f
    JOIN dim_carrier c ON f.carrier_id = c.carrier_id
    GROUP BY c.carrier_tier
),
totals AS (
    SELECT
        SUM(defect_yes) AS total_yes,
        SUM(defect_no) AS total_no,
        SUM(row_total) AS grand_total
    FROM observed
),
expected AS (
    SELECT
        o.carrier_tier,
        o.defect_yes AS obs_yes,
        o.defect_no AS obs_no,
        o.row_total * t.total_yes::DOUBLE / t.grand_total AS exp_yes,
        o.row_total * t.total_no::DOUBLE / t.grand_total AS exp_no
    FROM observed o
    CROSS JOIN totals t
)
SELECT
    'Chi-square test: Defect vs Carrier Tier' AS test_name,
    ROUND(SUM(
        (obs_yes - exp_yes) * (obs_yes - exp_yes) / exp_yes +
        (obs_no - exp_no) * (obs_no - exp_no) / exp_no
    ), 3) AS chi_square_statistic,
    3 AS degrees_of_freedom,
    7.815 AS critical_value_alpha_05,
    CASE
        WHEN SUM(
            (obs_yes - exp_yes) * (obs_yes - exp_yes) / exp_yes +
            (obs_no - exp_no) * (obs_no - exp_no) / exp_no
        ) > 7.815
        THEN 'REJECT H0: Defect rate depends on carrier tier (p < 0.05)'
        ELSE 'FAIL TO REJECT H0: Defect rate is independent of tier'
    END AS conclusion
FROM expected;
