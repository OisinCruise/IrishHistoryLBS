-- Initialize PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create postgis schema if not exists
CREATE SCHEMA IF NOT EXISTS postgis;

-- Verify PostGIS installation
SELECT postgis_version() AS postgis_version;
SELECT extension_schema, version FROM information_schema.constraint_column_usage
  WHERE constraint_schema = 'postgis';

-- Grant permissions
GRANT USAGE ON SCHEMA postgis TO PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA postgis TO PUBLIC;