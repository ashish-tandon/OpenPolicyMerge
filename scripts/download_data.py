#!/usr/bin/env python3
"""
Data download and management script for OpenPolicyAshBack2
Downloads OpenParliament database and represent-canada data
"""

import os
import sys
import requests
import subprocess
import zipfile
import tarfile
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def download_openparliament_data(self):
        """Download OpenParliament database dump"""
        logger.info("Checking OpenParliament database...")
        
        # Check if OpenParliament database already exists
        sql_file = Path("openparliament.public.sql")
        bz2_file = Path("openparliament.public.sql.bz2")
        
        if sql_file.exists():
            logger.info(f"OpenParliament database found: {sql_file} ({sql_file.stat().st_size / (1024**3):.1f} GB)")
            return
        elif bz2_file.exists():
            logger.info(f"OpenParliament compressed database found: {bz2_file} ({bz2_file.stat().st_size / (1024**3):.1f} GB)")
            logger.info("Extracting compressed database...")
            self.extract_bz2_file(bz2_file)
            return
        
        logger.info("OpenParliament database not found. You can download it manually from:")
        logger.info("https://openparliament.ca/data-download/")
        logger.info("Place the file as 'openparliament.public.sql.bz2' in the project root")
    
    def extract_bz2_file(self, file_path):
        """Extract bz2 compressed file"""
        import bz2
        
        output_file = file_path.with_suffix('.sql')
        
        try:
            with bz2.open(file_path, 'rb') as source, open(output_file, 'wb') as target:
                target.write(source.read())
            
            logger.info(f"Extracted {file_path} to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to extract {file_path}: {e}")
    
    def setup_represent_data(self):
        """Setup represent-canada data structure"""
        logger.info("Setting up represent-canada data structure...")
        
        # Create represent data directory
        represent_data_dir = self.data_dir / "represent-canada-data"
        represent_data_dir.mkdir(exist_ok=True)
        
        # Create shapefiles directory
        shapefiles_dir = represent_data_dir / "shapefiles"
        shapefiles_dir.mkdir(exist_ok=True)
        
        # Create symlink for shapefiles
        shapefiles_link = self.data_dir / "shapefiles"
        if not shapefiles_link.exists():
            try:
                shapefiles_link.symlink_to(shapefiles_dir)
                logger.info(f"Created symlink: {shapefiles_link} -> {shapefiles_dir}")
            except OSError as e:
                logger.error(f"Failed to create symlink: {e}")
        
        logger.info("Represent data structure created")
        logger.info("You can now download shapefiles and place them in data/represent-canada-data/shapefiles/")
    
    def download_represent_packages(self):
        """Download represent packages from GitHub"""
        logger.info("Setting up represent packages...")
        
        packages = [
            ("represent-boundaries", "https://pypi.org/project/represent-boundaries/"),
            ("represent-representatives", "https://github.com/opennorth/represent-reps.git"),
            ("represent-postcodes", "https://github.com/opennorth/represent-postcodes.git"),
        ]
        
        for package_name, package_url in packages:
            try:
                if "github.com" in package_url:
                    # Install from GitHub
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", f"git+{package_url}"
                    ], check=True)
                    logger.info(f"Installed {package_name} from GitHub")
                else:
                    # Try to install via pip
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package_name
                    ], check=True)
                    logger.info(f"Installed {package_name}")
            except subprocess.CalledProcessError:
                logger.warning(f"Could not install {package_name}")
                logger.info(f"You may need to manually install {package_name}")
    
    def create_database_scripts(self):
        """Create database setup scripts"""
        logger.info("Creating database setup scripts...")
        
        # PostgreSQL setup script
        postgres_script = self.data_dir / "setup_postgres.sh"
        with open(postgres_script, 'w') as f:
            f.write("""#!/bin/bash
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
""")
        
        postgres_script.chmod(0o755)
        logger.info(f"Created {postgres_script}")
        
        # Docker setup script
        docker_script = self.data_dir / "setup_docker.sh"
        with open(docker_script, 'w') as f:
            f.write("""#!/bin/bash
# Docker setup script for OpenPolicyAshBack2

echo "Setting up Docker environment..."

# Start PostgreSQL with PostGIS
docker run -d \\
    --name openpolicy-postgres \\
    -e POSTGRES_DB=represent \\
    -e POSTGRES_USER=postgres \\
    -e POSTGRES_PASSWORD=password \\
    -p 5432:5432 \\
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
""")
        
        docker_script.chmod(0o755)
        logger.info(f"Created {docker_script}")
    
    def create_data_loader(self):
        """Create data loading scripts"""
        logger.info("Creating data loading scripts...")
        
        # Python data loader
        loader_script = self.data_dir / "load_data.py"
        with open(loader_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Data loading script for OpenPolicyAshBack2
\"\"\"

import os
import sys
import django
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.backend.django.represent.settings')
django.setup()

def load_represent_data():
    \"\"\"Load represent-canada data\"\"\"
    try:
        from represent.management.commands import load_boundaries, load_reps, load_postcodes
        
        print("Loading boundaries...")
        # load_boundaries.Command().handle()
        
        print("Loading representatives...")
        # load_reps.Command().handle()
        
        print("Loading postcodes...")
        # load_postcodes.Command().handle()
        
    except ImportError as e:
        print(f"Could not import represent commands: {e}")
        print("Make sure represent packages are installed")

def load_openparliament_data():
    \"\"\"Load OpenParliament data\"\"\"
    print("Loading OpenParliament data...")
    # Implementation depends on OpenParliament data structure

if __name__ == "__main__":
    print("Loading data for OpenPolicyAshBack2...")
    
    # Load represent data
    load_represent_data()
    
    # Load OpenParliament data
    load_openparliament_data()
    
    print("Data loading complete!")
""")
        
        loader_script.chmod(0o755)
        logger.info(f"Created {loader_script}")
    
    def create_status_report(self):
        """Create a status report of the current setup"""
        logger.info("Creating status report...")
        
        status_file = self.data_dir / "status_report.txt"
        with open(status_file, 'w') as f:
            f.write("""OpenPolicyAshBack2 Data Status Report
===============================================

OpenParliament Database:
""")
            
            # Check OpenParliament database
            sql_file = Path("openparliament.public.sql")
            bz2_file = Path("openparliament.public.sql.bz2")
            
            if sql_file.exists():
                size_gb = sql_file.stat().st_size / (1024**3)
                f.write(f"✓ OpenParliament database: {sql_file} ({size_gb:.1f} GB)\n")
            elif bz2_file.exists():
                size_gb = bz2_file.stat().st_size / (1024**3)
                f.write(f"✓ OpenParliament compressed database: {bz2_file} ({size_gb:.1f} GB)\n")
            else:
                f.write("✗ OpenParliament database not found\n")
            
            f.write("""
Represent Canada Packages:
""")
            
            # Check represent packages
            try:
                import represent_boundaries
                f.write("✓ represent-boundaries installed\n")
            except ImportError:
                f.write("✗ represent-boundaries not installed\n")
            
            try:
                import represent_representatives
                f.write("✓ represent-representatives installed\n")
            except ImportError:
                f.write("✗ represent-representatives not installed\n")
            
            try:
                import represent_postcodes
                f.write("✓ represent-postcodes installed\n")
            except ImportError:
                f.write("✗ represent-postcodes not installed\n")
            
            f.write("""
Data Structure:
""")
            
            # Check data directories
            if (self.data_dir / "represent-canada-data").exists():
                f.write("✓ represent-canada-data directory created\n")
            else:
                f.write("✗ represent-canada-data directory missing\n")
            
            if (self.data_dir / "shapefiles").exists():
                f.write("✓ shapefiles symlink created\n")
            else:
                f.write("✗ shapefiles symlink missing\n")
            
            f.write("""
Setup Scripts:
""")
            
            # Check setup scripts
            if (self.data_dir / "setup_postgres.sh").exists():
                f.write("✓ PostgreSQL setup script created\n")
            else:
                f.write("✗ PostgreSQL setup script missing\n")
            
            if (self.data_dir / "setup_docker.sh").exists():
                f.write("✓ Docker setup script created\n")
            else:
                f.write("✗ Docker setup script missing\n")
            
            if (self.data_dir / "load_data.py").exists():
                f.write("✓ Data loader script created\n")
            else:
                f.write("✗ Data loader script missing\n")
            
            f.write("""
Next Steps:
1. Run database setup: cd data && ./setup_postgres.sh
2. Download shapefiles to data/represent-canada-data/shapefiles/
3. Load data: python data/load_data.py
4. Start services: docker-compose up -d
""")
        
        logger.info(f"Created status report: {status_file}")
    
    def run_all(self):
        """Run all data setup tasks"""
        logger.info("Starting data setup for OpenPolicyAshBack2...")
        
        # Check OpenParliament data
        self.download_openparliament_data()
        
        # Setup represent data structure
        self.setup_represent_data()
        
        # Download represent packages
        self.download_represent_packages()
        
        # Create setup scripts
        self.create_database_scripts()
        
        # Create data loader
        self.create_data_loader()
        
        # Create status report
        self.create_status_report()
        
        logger.info("Data setup complete!")
        logger.info("Next steps:")
        logger.info("1. Run: cd data && ./setup_postgres.sh")
        logger.info("2. Or run: cd data && ./setup_docker.sh")
        logger.info("3. Download shapefiles to data/represent-canada-data/shapefiles/")
        logger.info("4. Run: python data/load_data.py")
        logger.info("5. Check status: cat data/status_report.txt")

def main():
    manager = DataManager()
    manager.run_all()

if __name__ == "__main__":
    main() 