#!/bin/bash
echo "🚀 Starting OpenPolicy Scraper Service..."
source venv/bin/activate
export PYTHONPATH=.
python -c "
import asyncio
from src.services.scraper_manager import ScraperManager
from src.services.performance_monitor import PerformanceMonitor

async def start_service():
    print('Starting scraper manager...')
    async with ScraperManager() as manager:
        print('✅ Scraper manager started successfully')
        print('Service is now running and ready to accept requests')
        print('Press Ctrl+C to stop')
        
        # Keep service running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print('\n🛑 Service stopped by user')

if __name__ == '__main__':
    asyncio.run(start_service())
"
