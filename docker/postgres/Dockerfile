FROM postgis/postgis:14-3.3-alpine

COPY init.sql /docker-entrypoint-initdb.d/

LABEL maintainer="Oisin Cruise <oisincruise@gmail.com>" \
      description="PostgreSQL 14 with PostGIS 3.3 for Irish Civil War LBS" \
      version="1.0.0"
