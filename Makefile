.PHONY: install data build kpis anomalies forecast pricing excel test app clean all

install:
	pip install -r requirements.txt

data:
	python -m src.generate_data

build:
	python -m src.build_warehouse

kpis:
	python -m src.compute_kpis

anomalies:
	python -m src.anomaly_detection

forecast:
	python -m src.forecasting

pricing:
	python -m src.pricing_recommendations

excel:
	python -m src.excel_pivot_pack

test:
	pytest -v

app:
	streamlit run app/streamlit_app.py

clean:
	rm -rf data/raw/*.csv data/warehouse.duckdb reports/*.csv reports/*.xlsx reports/*.png reports/daily_briefings/*.md

all: install data build kpis anomalies forecast pricing excel test
