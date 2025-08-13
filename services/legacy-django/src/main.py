"""
Main entry point for Legacy Django Service
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'represent.settings')

# Configure Django
django.setup()

def main():
    """Main entry point"""
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
