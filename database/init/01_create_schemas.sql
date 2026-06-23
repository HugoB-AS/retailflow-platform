-- RetailFlow - Database schemas
-- Database: retailflow_db

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS governance;

COMMENT ON SCHEMA raw IS 'Raw events and unprocessed incoming data';
COMMENT ON SCHEMA core IS 'Clean business entities: customers, products, orders, payments';
COMMENT ON SCHEMA analytics IS 'Aggregated data, ML features, predictions and KPIs';
COMMENT ON SCHEMA governance IS 'Data governance, quality logs, retention policies and audit tables';
