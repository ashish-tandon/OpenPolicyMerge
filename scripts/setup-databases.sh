#!/bin/bash
# Comprehensive database setup for OpenPolicy platform

set -e

echo "🚀 Setting up OpenPolicy Platform Databases..."

# Configuration
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}

# Set PGPASSWORD for psql commands
export PGPASSWORD=$POSTGRES_PASSWORD

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if PostgreSQL is running
check_postgres() {
    print_status "Checking PostgreSQL connection..."
    
    if PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER > /dev/null 2>&1; then
        print_status "PostgreSQL is running and accessible"
        return 0
    else
        print_error "PostgreSQL is not accessible at $POSTGRES_HOST:$POSTGRES_PORT"
        return 1
    fi
}

# Function to create database
create_database() {
    local db_name=$1
    local schema_file=$2
    
    print_status "Creating database: $db_name"
    
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1; then
        print_warning "Database $db_name already exists"
    else
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $db_name;"
        print_status "Database $db_name created successfully"
    fi
    
    # Initialize schema if provided
    if [ ! -z "$schema_file" ] && [ -f "$schema_file" ]; then
        print_status "Initializing schema for $db_name from $schema_file"
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $db_name -f $schema_file
        print_status "Schema initialized for $db_name"
    fi
}

# Function to setup database extensions
setup_extensions() {
    local db_name=$1
    
    print_status "Setting up extensions for $db_name"
    
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $db_name <<-EOSQL
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE EXTENSION IF NOT EXISTS "pg_trgm";
        CREATE EXTENSION IF NOT EXISTS "btree_gin";
        CREATE EXTENSION IF NOT EXISTS "postgis";
EOSQL
    
    print_status "Extensions setup complete for $db_name"
}

# Function to create schemas in main database
create_schemas() {
    local db_name=$1
    
    print_status "Creating service schemas in $db_name"
    
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $db_name <<-EOSQL
        -- Core service schemas
        CREATE SCHEMA IF NOT EXISTS auth;
        CREATE SCHEMA IF NOT EXISTS etl;
        CREATE SCHEMA IF NOT EXISTS plotly;
        CREATE SCHEMA IF NOT EXISTS go;
        CREATE SCHEMA IF NOT EXISTS scrapers;
        CREATE SCHEMA IF NOT EXISTS health;
        CREATE SCHEMA IF NOT EXISTS monitoring;
        CREATE SCHEMA IF NOT EXISTS notifications;
        CREATE SCHEMA IF NOT EXISTS config;
        CREATE SCHEMA IF NOT EXISTS search;
        CREATE SCHEMA IF NOT EXISTS policy;
        
        -- Grant permissions
        GRANT USAGE ON SCHEMA auth TO postgres;
        GRANT USAGE ON SCHEMA etl TO postgres;
        GRANT USAGE ON SCHEMA plotly TO postgres;
        GRANT USAGE ON SCHEMA go TO postgres;
        GRANT USAGE ON SCHEMA scrapers TO postgres;
        GRANT USAGE ON SCHEMA health TO postgres;
        GRANT USAGE ON SCHEMA monitoring TO postgres;
        GRANT USAGE ON SCHEMA notifications TO postgres;
        GRANT USAGE ON SCHEMA config TO postgres;
        GRANT USAGE ON SCHEMA search TO postgres;
        GRANT USAGE ON SCHEMA policy TO postgres;
EOSQL
    
    print_status "Service schemas created successfully in $db_name"
}

# Main setup process
main() {
    print_status "Starting OpenPolicy database setup..."
    
    # Check PostgreSQL connection
    if ! check_postgres; then
        print_error "Cannot proceed without PostgreSQL connection"
        exit 1
    fi
    
    # Create main openpolicy database with scraper data
    create_database "openpolicy" "db/schema-scraper-data.sql"
    setup_extensions "openpolicy"
    
    # Create service schemas within the main database
    create_schemas "openpolicy"
    
    print_status "Database setup complete!"
    print_status "Consolidated approach: 1 database with multiple schemas"
    print_status "Available schemas in 'openpolicy' database:"
    print_status "  - federal, provincial, municipal (data schemas)"
    print_status "  - auth, etl, plotly, go, scrapers, health, monitoring"
    print_status "  - notifications, config, search, policy (service schemas)"
    
    # Show database info
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c "\l" | grep openpolicy
}

# Run main function
main "$@"
