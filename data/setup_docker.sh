#!/bin/bash
# Docker setup script for OpenPolicyAshBack2

echo "Setting up Docker environment..."

# Start PostgreSQL with PostGIS
docker run -d \
    --name openpolicy-postgres \
    -e POSTGRES_DB=represent \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=password \
    -p 5432:5432 \
    postgis/postgis:15-3.3

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Import data if available
if [ -f "../openparliament.public.sql" ]; then
    echo "Importing OpenParliament data..."
    docker exec -i openpolicy-postgres psql -U postgres -d represent < ../openparliament.public.sql
fi

echo "Docker setup complete!"
