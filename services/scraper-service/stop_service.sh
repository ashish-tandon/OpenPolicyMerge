#!/bin/bash
echo "🛑 Stopping OpenPolicy Scraper Service..."
pkill -f "start_service.sh" || true
pkill -f "python.*scraper" || true
echo "✅ Service stopped"
