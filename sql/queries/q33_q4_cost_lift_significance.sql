-- Query: q33_q4_cost_lift_significance
-- Business question: Is the Q4 cost-per-mile increase statistically significant
--   compared to non-Q4 months?
-- Returns: Mann-Whitney U test via rank-sum approximation.
-- Usage: duckdb data/warehouse.duckdb < sql/queries/q33_q4_cost_lift_significance.sql
-- Techniques: CTE, RANK window function, normal approximation for U-statistic

-- Mann-Whitney U test: compare Q4 vs non-Q4 cost-per-mile distributions.
-- Uses rank-sum with normal approximation (valid for large n).

WITH ranked AS (
    SELECT
        CASE WHEN d.month IN (10, 11, 12) THEN 'Q4' ELSE 'Non-Q4' END AS period,
        f.total_cost_usd / NULLIF(f.distance_miles, 0) AS cpm,
        RANK() OVER (ORDER BY f.total_cost_usd / NULLIF(f.distance_miles, 0)) AS overall_rank
    FROM fact_shipment f
    JOIN dim_date d ON f.shipment_date_key = d.date_key
    WHERE f.distance_miles > 0
),
group_stats AS (
    SELECT
        period,
        COUNT(*) AS n,
        SUM(overall_rank) AS rank_sum,
        AVG(cpm) AS mean_cpm
    FROM ranked
    GROUP BY period
),
test_calc AS (
    SELECT
        q4.n AS n1,
        nq4.n AS n2,
        q4.rank_sum AS R1,
        q4.rank_sum - q4.n * (q4.n + 1.0) / 2.0 AS U1,
        q4.n::DOUBLE * nq4.n - (q4.rank_sum - q4.n * (q4.n + 1.0) / 2.0) AS U2,
        q4.n::DOUBLE * nq4.n / 2.0 AS mu_U,
        SQRT(q4.n::DOUBLE * nq4.n * (q4.n + nq4.n + 1.0) / 12.0) AS sigma_U,
        q4.mean_cpm AS q4_mean_cpm,
        nq4.mean_cpm AS nonq4_mean_cpm
    FROM group_stats q4, group_stats nq4
    WHERE q4.period = 'Q4' AND nq4.period = 'Non-Q4'
)
SELECT
    n1 AS q4_sample_size,
    n2 AS nonq4_sample_size,
    ROUND(q4_mean_cpm, 2) AS q4_avg_cpm,
    ROUND(nonq4_mean_cpm, 2) AS nonq4_avg_cpm,
    ROUND(U1, 0) AS u_statistic,
    ROUND((U1 - mu_U) / NULLIF(sigma_U, 0), 3) AS z_score,
    1.96 AS critical_value_alpha_05,
    CASE
        WHEN ABS((U1 - mu_U) / NULLIF(sigma_U, 0)) > 1.96
        THEN 'REJECT H0: Q4 cost-per-mile is significantly different (p < 0.05)'
        ELSE 'FAIL TO REJECT H0: No significant difference'
    END AS conclusion
FROM test_calc;
