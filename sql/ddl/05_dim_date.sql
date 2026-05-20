-- DDL: dim_date
-- Date dimension for time-series analysis.

CREATE TABLE IF NOT EXISTS dim_date (
    date_key        INTEGER PRIMARY KEY,    -- YYYYMMDD format
    date            DATE NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    week_of_year    INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,       -- 0=Monday, 6=Sunday
    is_weekend      BOOLEAN NOT NULL,
    is_holiday      BOOLEAN NOT NULL,
    is_peak_season  BOOLEAN NOT NULL
);
