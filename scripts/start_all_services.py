#!/usr/bin/env python3
"""
Start All OpenPolicy Platform Services
This script starts all services concurrently for development and testing.
"""

import asyncio
import subprocess
import time
import signal
import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Service configurations
SERVICES = {
    'policy-service': {
        'port': 8001,
        'path': 'services/policy-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8001', '--reload']
    },
    'search-service': {
        'port': 8002,
        'path': 'services/search-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8002', '--reload']
    },
    'auth-service': {
        'port': 8003,
        'path': 'services/auth-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8003', '--reload']
    },
    'notification-service': {
        'port': 8004,
        'path': 'services/notification-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8004', '--reload']
    },
    'config-service': {
        'port': 8005,
        'path': 'services/config-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8005', '--reload']
    },
    'health-service': {
        'port': 8006,
        'path': 'services/health-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8006', '--reload']
    },
    'etl-service': {
        'port': 8007,
        'path': 'services/etl',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8007', '--reload']
    },
    'scraper-service': {
        'port': 8008,
        'path': 'services/scraper-service',
        'command': ['python', '-m', 'uvicorn', 'src.api:app', '--host', '0.0.0.0', '--port', '8008', '--reload']
    }
}

# Store process references
processes = {}

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("Shutting down all services...")
    stop_all_services()
    sys.exit(0)

def stop_all_services():
    """Stop all running services."""
    for service_name, process in processes.items():
        if process and process.poll() is None:
            logger.info(f"Stopping {service_name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name}")
                process.kill()
            logger.info(f"{service_name} stopped")

def start_service(service_name, service_config):
    """Start a single service."""
    try:
        # Change to service directory
        service_path = Path(service_config['path'])
        if not service_path.exists():
            logger.error(f"Service path does not exist: {service_path}")
            return None
        
        # Check if requirements.txt exists and install dependencies
        requirements_file = service_path / 'requirements.txt'
        if requirements_file.exists():
            logger.info(f"Installing dependencies for {service_name}...")
            try:
                subprocess.run([
                    'pip', 'install', '-r', str(requirements_file)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install dependencies for {service_name}: {e}")
        
        # Start the service
        logger.info(f"Starting {service_name} on port {service_config['port']}...")
        
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = str(service_path)
        
        # Start the process
        process = subprocess.Popen(
            service_config['command'],
            cwd=service_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        if process.poll() is None:
            logger.info(f"✅ {service_name} started successfully (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ {service_name} failed to start:")
            if stdout:
                logger.error(f"STDOUT: {stdout}")
            if stderr:
                logger.error(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to start {service_name}: {e}")
        return None

def check_service_health(service_name, port):
    """Check if a service is responding to health checks."""
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/healthz", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def start_all_services():
    """Start all services concurrently."""
    logger.info("🚀 Starting OpenPolicy Platform Services...")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start each service
    for service_name, service_config in SERVICES.items():
        process = start_service(service_name, service_config)
        if process:
            processes[service_name] = process
        else:
            logger.error(f"Failed to start {service_name}")
    
    # Wait for services to be ready
    logger.info("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Check service health
    healthy_services = 0
    for service_name, service_config in SERVICES.items():
        if check_service_health(service_name, service_config['port']):
            logger.info(f"✅ {service_name} is healthy")
            healthy_services += 1
        else:
            logger.warning(f"⚠️ {service_name} health check failed")
    
    logger.info(f"🎉 Started {healthy_services}/{len(SERVICES)} services successfully!")
    
    if healthy_services == len(SERVICES):
        logger.info("🎯 All services are running and healthy!")
        logger.info("📚 API Documentation available at:")
        for service_name, service_config in SERVICES.items():
            logger.info(f"   {service_name}: http://localhost:{service_config['port']}/docs")
    else:
        logger.warning("⚠️ Some services failed to start or are unhealthy")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
            # Check if any processes have died
            for service_name, process in list(processes.items()):
                if process.poll() is not None:
                    logger.error(f"❌ {service_name} has stopped unexpectedly")
                    # Restart the service
                    logger.info(f"🔄 Restarting {service_name}...")
                    new_process = start_service(service_name, SERVICES[service_name])
                    if new_process:
                        processes[service_name] = new_process
                        logger.info(f"✅ {service_name} restarted successfully")
                    else:
                        logger.error(f"❌ Failed to restart {service_name}")
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        stop_all_services()

if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("services").exists():
        logger.error("Please run this script from the OpenPolicyMerge root directory")
        sys.exit(1)
    
    start_all_services()
