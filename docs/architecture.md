# Architecture

## Data Flow

```
src/config.py (benchmarks)
       |
src/generate_data.py
       |
  data/raw/*.csv (6 CSV files)
       |
src/build_warehouse.py + sql/ddl/*.sql
       |
  data/warehouse.duckdb
       |
  +-- sql/views/*.sql (6 materialized views)
  |
  +-- sql/queries/*.sql (35 executable queries)
  |
  +-- src/compute_kpis.py --> reports/*.csv
  |
  +-- src/anomaly_detection.py --> data/raw/anomalies_*.csv + reports/daily_briefings/*.md
  |
  +-- src/forecasting.py --> reports/forecast_*.{csv,png}
  |
  +-- src/pricing_recommendations.py --> reports/pricing_recommendations.csv
  |
  +-- src/excel_pivot_pack.py --> reports/pivot_pack.xlsx
  |
  +-- app/streamlit_app.py (reads warehouse + reports)
  |
  +-- tableau/tableau_extract.csv (for Tableau Public)
```

## Design Decisions

1. **DuckDB over SQLite/Postgres:** Zero-config, columnar OLAP engine. A recruiter clones the repo and runs `make all` without installing a database server. Production equivalent would be Redshift or BigQuery.

2. **Star schema over flat file:** Demonstrates data modeling competency. Five conformed dimensions (carrier, lane, shipper, date, service type) with a single fact table at shipment grain.

3. **Decimal for currency:** All cost columns use Python `decimal.Decimal` during generation and DuckDB `DECIMAL(10,2)` for storage. The cost identity `linehaul + fuel + accessorial = total` holds exactly across 1M+ rows with zero tolerance.

4. **Synthetic data over real data:** Real freight data is proprietary. Synthetic data calibrated to public benchmarks (FreightWaves, Cass, ATRI, BTS) demonstrates the same analytical skills while being freely distributable.

5. **SARIMAX over Prophet:** Smaller dependency footprint, statistical pedigree (Box-Jenkins), interpretable parameters, and better suited for a BA portfolio than a black-box ML model.
