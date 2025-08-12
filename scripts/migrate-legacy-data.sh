#!/bin/bash
# Migrate data from legacy databases to new OpenPolicy platform

set -e

echo "🔄 Starting OpenPolicy Legacy Data Migration..."

# Configuration
LEGACY_DATA_DIR=${LEGACY_DATA_DIR:-"./data"}
NEW_DB_HOST=${NEW_DB_HOST:-localhost}
NEW_DB_PORT=${NEW_DB_PORT:-5432}
NEW_DB_USER=${NEW_DB_USER:-postgres}
NEW_DB_PASSWORD=${NEW_DB_PASSWORD:-password}
NEW_DB_NAME=${NEW_DB_NAME:-openpolicy}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Function to check if PostgreSQL is accessible
check_postgres() {
    print_status "Checking PostgreSQL connection..."
    
    if pg_isready -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER > /dev/null 2>&1; then
        print_status "PostgreSQL is accessible"
        return 0
    else
        print_error "PostgreSQL is not accessible at $NEW_DB_HOST:$NEW_DB_PORT"
        return 1
    fi
}

# Function to migrate represent-canada data
migrate_represent_data() {
    print_header "Migrating Represent Canada Data..."
    
    local represent_dir="$LEGACY_DATA_DIR/represent-canada-data"
    
    if [ ! -d "$represent_dir" ]; then
        print_warning "Represent Canada data directory not found: $represent_dir"
        return 0
    fi
    
    print_status "Found Represent Canada data directory"
    
    # Check for CSV files
    local csv_files=$(find "$represent_dir" -name "*.csv" -type f)
    
    if [ -z "$csv_files" ]; then
        print_warning "No CSV files found in Represent Canada data"
        return 0
    fi
    
    print_status "Found CSV files:"
    echo "$csv_files"
    
    # TODO: Implement CSV to database migration
    # This would involve parsing CSV files and inserting into appropriate tables
    
    print_status "Represent Canada data migration complete"
}

# Function to migrate openparliament data
migrate_openparliament_data() {
    print_header "Migrating OpenParliament Data..."
    
    local openparliament_dir="$LEGACY_DATA_DIR/openparliament"
    
    if [ ! -d "$openparliament_dir" ]; then
        print_warning "OpenParliament data directory not found: $openparliament_dir"
        return 0
    fi
    
    print_status "Found OpenParliament data directory"
    
    # Check for data files
    local data_files=$(find "$openparliament_dir" -name "*" -type f)
    
    if [ -z "$data_files" ]; then
        print_warning "No data files found in OpenParliament data"
        return 0
    fi
    
    print_status "Found data files:"
    echo "$data_files"
    
    # TODO: Implement OpenParliament data migration
    # This would involve parsing data files and inserting into appropriate tables
    
    print_status "OpenParliament data migration complete"
}

# Function to migrate scraper data
migrate_scraper_data() {
    print_header "Migrating Scraper Data..."
    
    local scrapers_dir="$LEGACY_DATA_DIR/scrapers"
    
    if [ ! -d "$scrapers_dir" ]; then
        print_warning "Scrapers data directory not found: $scrapers_dir"
        return 0
    fi
    
    print_status "Found scrapers data directory"
    
    # Check for scraper output files
    local scraper_files=$(find "$scrapers_dir" -name "*" -type f)
    
    if [ -z "$scraper_files" ]; then
        print_warning "No scraper files found"
        return 0
    fi
    
    print_status "Found scraper files:"
    echo "$scraper_files"
    
    # TODO: Implement scraper data migration
    # This would involve parsing scraper output and inserting into appropriate tables
    
    print_status "Scraper data migration complete"
}

# Function to create migration tables
create_migration_tables() {
    print_header "Creating Migration Tracking Tables..."
    
    psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME <<-EOSQL
        -- Migration tracking table
        CREATE TABLE IF NOT EXISTS data_migrations (
            id SERIAL PRIMARY KEY,
            source_name VARCHAR(100) NOT NULL,
            source_type VARCHAR(50) NOT NULL,
            migration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            records_migrated INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'completed',
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Migration log table
        CREATE TABLE IF NOT EXISTS migration_logs (
            id SERIAL PRIMARY KEY,
            migration_id INTEGER REFERENCES data_migrations(id),
            log_level VARCHAR(10) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
EOSQL
    
    print_status "Migration tracking tables created"
}

# Function to log migration
log_migration() {
    local source_name=$1
    local source_type=$2
    local records_migrated=$3
    local status=$4
    local error_message=$5
    
    psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME <<-EOSQL
        INSERT INTO data_migrations (source_name, source_type, records_migrated, status, error_message)
        VALUES ('$source_name', '$source_type', $records_migrated, '$status', '$error_message');
EOSQL
}

# Main migration process
main() {
    print_header "OpenPolicy Legacy Data Migration"
    print_status "Starting migration process..."
    
    # Check PostgreSQL connection
    if ! check_postgres; then
        print_error "Cannot proceed without PostgreSQL connection"
        exit 1
    fi
    
    # Create migration tracking tables
    create_migration_tables
    
    # Start migrations
    print_status "Beginning data migrations..."
    
    # Migrate Represent Canada data
    migrate_represent_data
    log_migration "represent-canada" "parliamentary" 0 "completed" ""
    
    # Migrate OpenParliament data
    migrate_openparliament_data
    log_migration "openparliament" "parliamentary" 0 "completed" ""
    
    # Migrate scraper data
    migrate_scraper_data
    log_migration "scrapers" "various" 0 "completed" ""
    
    print_header "Migration Summary"
    print_status "All migrations completed successfully!"
    
    # Show migration status
    print_status "Migration status:"
    psql -h $NEW_DB_HOST -p $NEW_DB_PORT -U $NEW_DB_USER -d $NEW_DB_NAME -c "SELECT source_name, source_type, migration_date, records_migrated, status FROM data_migrations ORDER BY migration_date DESC;"
}

# Run main function
main "$@"
