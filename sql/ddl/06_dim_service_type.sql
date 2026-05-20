-- DDL: dim_service_type
-- Service type dimension for modal analysis.

CREATE TABLE IF NOT EXISTS dim_service_type (
    service_type_id         INTEGER PRIMARY KEY,
    service_name            VARCHAR NOT NULL,     -- FTL / LTL / Intermodal
    transit_time_sla_hours  INTEGER NOT NULL,
    target_otp_pct          DOUBLE NOT NULL,
    target_defect_rate_pct  DOUBLE NOT NULL
);
