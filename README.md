# Inbound First-Mile Carrier Performance Dashboard

An end-to-end analytics stack for inbound first-mile transportation: a 1M+ shipment synthetic data warehouse, 35 SQL queries, anomaly detection, SARIMAX forecasting, pricing recommendations, and dashboards in Streamlit and Tableau.

## Live Demos

- **Streamlit Dashboard:** [Coming soon -- deploy via `streamlit run app/streamlit_app.py`]
- **Tableau Public:** [Coming soon -- see `tableau/README.md`]

## Tech Stack

Python | DuckDB | Streamlit | Plotly | Tableau | statsmodels | openpyxl | pytest | ruff

## Quickstart

```bash
git clone <repo-url>
cd first-mile-carrier-dashboard
make all    # generates data, builds warehouse, runs analytics, tests
make app    # launches Streamlit at localhost:8501
```

## Architecture

```
Synthetic Data Generator (config.py benchmarks)
    |
    v
CSV Files (data/raw/)
    |
    v
DuckDB Star Schema (data/warehouse.duckdb)
    |
    +---> SQL Views (6 materialized views)
    +---> SQL Queries (35 executable queries)
    +---> Anomaly Detection (z-score + IQR)
    +---> SARIMAX Forecasting (OTP + Cost)
    +---> Pricing Recommendations (top-20 shippers)
    +---> Excel Pivot Pack (6-sheet .xlsx)
    +---> Streamlit Dashboard (6 pages)
    +---> Tableau Extract (CSV for Tableau Public)
```

## What's Inside

| Directory | Contents |
|---|---|
| `src/` | Data generation, warehouse build, anomaly detection, forecasting, pricing, KPI computation, Excel pivot pack |
| `sql/ddl/` | 6 DDL files defining the star schema |
| `sql/views/` | 6 analytical views including Shipper Health Score |
| `sql/queries/` | 35 numbered SQL queries across operations, cost, utilization, network, anomaly, and statistical testing |
| `app/` | 6-page Streamlit dashboard with What-If Simulator |
| `reports/` | Generated outputs: forecasts, pricing recs, daily briefings, pivot pack |
| `tableau/` | Extract CSV and Tableau Public instructions |
| `vba/` | Sample VBA macro for Excel pivot refresh |
| `tests/` | pytest suite validating data integrity, anomaly detection, forecasting, and Excel output |
| `docs/` | Data dictionary, KPI definitions, architecture, methodology, interview prep |

## KPI Definitions

See [docs/kpi_definitions.md](docs/kpi_definitions.md) for precise computation formulas for all 15 KPIs.

## Data Dictionary

See [docs/data_dictionary.md](docs/data_dictionary.md) for complete table and column documentation.

## Methodology -- Why This Isn't Toy Data

The data in this project is synthetic, but calibrated to public industry benchmarks:

- **On-time pickup baseline (87%):** FreightWaves SONAR On-Time Pickup Index (OTPI), 2024
- **Dwell time distribution (median 45min, P90 120min):** Trucker Tools 2024 Detention Study
- **Trailer utilization (78% FTL, 64% LTL, 85% Intermodal):** ATRI 2024 Operational Costs of Trucking
- **Linehaul cost ($2.43/mile base):** Cass Information Systems Freight Index, 2024
- **Modal split (FTL 62%, LTL 28%, Intermodal 10%):** ATA/BTS 2024 modal split for inbound contract freight
- **Shipper concentration (top-20 = ~55%):** FreightWaves SONAR Shipper Concentration Index, 2024

**Limitations:** No real carrier reputations, no actual regulatory complexity, no real shipper relationships. Lane distances are randomized within realistic ranges rather than computed from geographic coordinates. A production version would use real carrier scorecards, actual contract rates, and operational data feeds.

Every benchmark constant is cited in `src/config.py` with its source on the line above.

## License

MIT -- see [LICENSE](LICENSE).
