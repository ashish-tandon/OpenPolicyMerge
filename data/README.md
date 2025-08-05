# Data Directory

This directory contains data files for the OpenPolicy Merge project.

## Database Files

The OpenParliament database files are not included in this repository due to their large size (6.5GB uncompressed). To download them:

### Option 1: Download from OpenParliament
1. Visit: https://openparliament.ca/data-download/
2. Download the latest database dump
3. Extract and place in this directory

### Option 2: Use the provided script
```bash
# Run the data management script
python scripts/download_data.py
```

### Option 3: Manual download
```bash
# Download the compressed database
curl -L -o openparliament.public.sql.bz2 https://openparliament.ca/data-download/openparliament.public.sql.bz2

# Extract the database
bunzip2 openparliament.public.sql.bz2
```

## Shapefiles for Represent Canada

The electoral boundary shapefiles are also not included due to size. To set them up:

1. Download shapefiles from various government sources
2. Place them in `data/represent-canada-data/shapefiles/`
3. Run the setup script: `python scripts/download_data.py`

## Database Setup

After downloading the database files, run:

```bash
# Setup PostgreSQL database
cd data && ./setup_postgres.sh

# Or for Docker
cd data && ./setup_docker.sh
```

## Data Loading

Load the data into the database:

```bash
# Load OpenParliament data
python data/load_data.py

# Or manually
psql -U postgres -d openparliament -f openparliament.public.sql
```

## File Structure

```
data/
├── README.md                    # This file
├── setup_postgres.sh           # PostgreSQL setup script
├── setup_docker.sh             # Docker setup script
├── load_data.py                # Data loading script
├── status_report.txt           # Data status report
├── represent-canada-data/      # Represent Canada data (not in repo)
│   └── shapefiles/            # Electoral boundary shapefiles
└── shapefiles/                # Symlink to represent-canada-data/shapefiles
```

## Notes

- Database files are excluded from git due to size limits
- Shapefiles are excluded due to size and licensing considerations
- Use the provided scripts for automated setup
- Check `status_report.txt` for current data status 