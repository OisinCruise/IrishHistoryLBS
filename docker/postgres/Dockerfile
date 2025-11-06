FROM --platform=linux/arm64/v8 postgres:14-bullseye

# Install PostGIS and dependencies
RUN apt-get update && apt-get install -y \
    postgresql-14-postgis-3 \
    postgresql-14-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*

# Enable PostGIS extension
RUN echo "CREATE EXTENSION IF NOT EXISTS postgis;" > /docker-entrypoint-initdb.d/postgis.sql

EXPOSE 5432
