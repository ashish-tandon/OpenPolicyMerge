#!/bin/bash
echo "🏥 Checking OpenPolicy Scraper Service Health..."
source venv/bin/activate
export PYTHONPATH=.
python system_status_report.py
