-- DDL: dim_lane
-- Lane dimension representing origin-destination pairs.

CREATE TABLE IF NOT EXISTS dim_lane (
    lane_id         INTEGER PRIMARY KEY,
    origin_city     VARCHAR NOT NULL,
    origin_state    VARCHAR NOT NULL,
    origin_zip3     VARCHAR NOT NULL,
    dest_city       VARCHAR NOT NULL,
    dest_state      VARCHAR NOT NULL,
    dest_zip3       VARCHAR NOT NULL,
    dest_fc_id      VARCHAR NOT NULL,
    distance_miles  DOUBLE NOT NULL,
    lane_type       VARCHAR NOT NULL    -- Short (<500mi) / Mid (500-1500mi) / Long (>1500mi)
);
