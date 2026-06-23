-- RetailFlow - Read-only database role
-- Database: retailflow_db
--
-- Purpose:
-- - Provide a least-privilege account for BI, dashboards, audit review and demos.
-- - Allow SELECT access to business schemas without allowing INSERT/UPDATE/DELETE.
-- - Keep the main retailflow role for application write workloads.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'retailflow_readonly'
    ) THEN
        CREATE ROLE retailflow_readonly LOGIN PASSWORD 'readonly';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE retailflow_db TO retailflow_readonly;

GRANT USAGE ON SCHEMA raw TO retailflow_readonly;
GRANT USAGE ON SCHEMA core TO retailflow_readonly;
GRANT USAGE ON SCHEMA analytics TO retailflow_readonly;
GRANT USAGE ON SCHEMA governance TO retailflow_readonly;

GRANT SELECT ON ALL TABLES IN SCHEMA raw TO retailflow_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA core TO retailflow_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO retailflow_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA governance TO retailflow_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA raw
GRANT SELECT ON TABLES TO retailflow_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA core
GRANT SELECT ON TABLES TO retailflow_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA analytics
GRANT SELECT ON TABLES TO retailflow_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA governance
GRANT SELECT ON TABLES TO retailflow_readonly;

COMMENT ON ROLE retailflow_readonly IS 'Read-only account for dashboards, BI, audit review and demo access.';
