CREATE SCHEMA IF NOT EXISTS marketing_ingestion_statistics;

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.ingestion_metadata (
    batch_id SERIAL,
    file_name TEXT,
    execution_timestamp TIMESTAMP,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.batch_columns_stats (
    id SERIAL,
    batch_id INT,
    num_expected_features INT,
    num_observed_features INT,
    num_new_features INT,
    num_missing_features INT,
    num_data_errors INT,
    num_samples INT,
    num_affected_samples INT,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.column_error_types (
    id SERIAL,
    batch_id INT,
    feature TEXT,
    col_error_type TEXT,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.feature_error_stats (
    id SERIAL,
    batch_id INT,
    feature TEXT,
    error_type TEXT,
    num_records INT,
    num_affected_records INT,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

