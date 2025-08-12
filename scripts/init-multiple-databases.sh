#!/bin/bash
# Initialize multiple PostgreSQL databases for OpenPolicy platform

set -e

# Database names
DATABASES=(
    "openpolicy"
    "openpolicy_etl"
    "openpolicy_plotly"
    "openpolicy_go"
    "openpolicy_scrapers"
    "openpolicy_health"
    "openpolicy_auth"
    "openpolicy_monitoring"
    "openpolicy_notifications"
    "openpolicy_config"
    "openpolicy_search"
    "openpolicy_policy"
)

# Create databases
for db in "${DATABASES[@]}"; do
    echo "Creating database: $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE DATABASE $db;
        GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
done

echo "All databases created successfully!"

# Initialize main openpolicy database with schema
echo "Initializing main openpolicy database with schema..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "openpolicy" -f /docker-entrypoint-initdb.d/schema.sql

echo "Database initialization complete!"
