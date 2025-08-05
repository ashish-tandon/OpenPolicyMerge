#!/bin/bash
# PostgreSQL setup script for OpenPolicyAshBack2

echo "Setting up PostgreSQL database..."

# Create database
createdb represent

# Enable PostGIS extension
psql -c "CREATE EXTENSION postgis;" represent

# Import OpenParliament data if available
if [ -f "../openparliament.public.sql" ]; then
    echo "Importing OpenParliament data..."
    psql represent < ../openparliament.public.sql
fi

echo "Database setup complete!"
