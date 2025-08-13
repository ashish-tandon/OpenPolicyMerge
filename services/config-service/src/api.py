"""
Configuration Service API - Complete Implementation
FastAPI application for centralized configuration management.
"""

from fastapi import FastAPI, Depends, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Configuration Service API",
    description="OpenPolicy Platform - Centralized Configuration Management Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ConfigItem(BaseModel):
    key: str = Field(..., description="Configuration key")
    value: Any = Field(..., description="Configuration value")
    description: Optional[str] = Field(None, description="Configuration description")
    category: Optional[str] = Field(None, description="Configuration category")
    is_encrypted: bool = Field(False, description="Whether value is encrypted")
    version: str = Field("1.0.0", description="Configuration version")

class ConfigUpdateRequest(BaseModel):
    value: Any = Field(..., description="New configuration value")
    description: Optional[str] = Field(None, description="Configuration description")
    category: Optional[str] = Field(None, description="Configuration category")
    is_encrypted: Optional[bool] = Field(None, description="Whether value is encrypted")

# In-memory configuration store (replace with database in production)
config_store = {
    "database.host": {"value": "localhost", "description": "Database host", "category": "database", "version": "1.0.0"},
    "database.port": {"value": 5432, "description": "Database port", "category": "database", "version": "1.0.0"},
    "database.name": {"value": "openpolicy", "description": "Database name", "category": "database", "version": "1.0.0"},
    "redis.host": {"value": "localhost", "description": "Redis host", "category": "cache", "version": "1.0.0"},
    "redis.port": {"value": 6379, "description": "Redis port", "category": "cache", "version": "1.0.0"},
    "api.timeout": {"value": 30, "description": "API timeout in seconds", "category": "api", "version": "1.0.0"},
    "logging.level": {"value": "INFO", "description": "Logging level", "category": "logging", "version": "1.0.0"}
}

# Health endpoints
@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "config-service",
        "version": "1.0.0"
    }

@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "service": "config-service"
    }

# Configuration endpoints
@app.get("/config", response_model=Dict[str, Any], tags=["Configuration"])
async def get_all_config(
    category: Optional[str] = Query(None, description="Filter by category"),
    include_encrypted: bool = Query(False, description="Include encrypted values")
):
    """Get all configuration items."""
    try:
        if category:
            filtered_config = {k: v for k, v in config_store.items() if v.get("category") == category}
        else:
            filtered_config = config_store.copy()
        
        if not include_encrypted:
            filtered_config = {k: v for k, v in filtered_config.items() if not v.get("is_encrypted", False)}
        
        return filtered_config
        
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")

@app.get("/config/{key}", response_model=ConfigItem, tags=["Configuration"])
async def get_config(key: str = Path(..., description="Configuration key")):
    """Get a specific configuration item."""
    try:
        if key not in config_store:
            raise HTTPException(status_code=404, detail="Configuration key not found")
        
        config_item = config_store[key]
        return ConfigItem(
            key=key,
            value=config_item["value"],
            description=config_item.get("description"),
            category=config_item.get("category"),
            is_encrypted=config_item.get("is_encrypted", False),
            version=config_item.get("version", "1.0.0")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get configuration {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")

@app.put("/config/{key}", response_model=ConfigItem, tags=["Configuration"])
async def update_config(
    key: str = Path(..., description="Configuration key"),
    request: ConfigUpdateRequest = None
):
    """Update a configuration item."""
    try:
        if key not in config_store:
            raise HTTPException(status_code=404, detail="Configuration key not found")
        
        # Update configuration
        if request.value is not None:
            config_store[key]["value"] = request.value
        if request.description is not None:
            config_store[key]["description"] = request.description
        if request.category is not None:
            config_store[key]["category"] = request.category
        if request.is_encrypted is not None:
            config_store[key]["is_encrypted"] = request.is_encrypted
        
        config_store[key]["updated_at"] = datetime.now()
        
        logger.info(f"Configuration updated: {key}")
        
        return ConfigItem(
            key=key,
            value=config_store[key]["value"],
            description=config_store[key].get("description"),
            category=config_store[key].get("category"),
            is_encrypted=config_store[key].get("is_encrypted", False),
            version=config_store[key].get("version", "1.0.0")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update configuration {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@app.post("/config", response_model=ConfigItem, status_code=201, tags=["Configuration"])
async def create_config(request: ConfigItem):
    """Create a new configuration item."""
    try:
        if request.key in config_store:
            raise HTTPException(status_code=400, detail="Configuration key already exists")
        
        config_store[request.key] = {
            "value": request.value,
            "description": request.description,
            "category": request.category,
            "is_encrypted": request.is_encrypted,
            "version": request.version,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        logger.info(f"Configuration created: {request.key}")
        
        return request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to create configuration")

@app.delete("/config/{key}", status_code=204, tags=["Configuration"])
async def delete_config(key: str = Path(..., description="Configuration key")):
    """Delete a configuration item."""
    try:
        if key not in config_store:
            raise HTTPException(status_code=404, detail="Configuration key not found")
        
        del config_store[key]
        
        logger.info(f"Configuration deleted: {key}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete configuration {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete configuration")

@app.get("/config/categories", response_model=List[str], tags=["Configuration"])
async def get_config_categories():
    """Get all configuration categories."""
    try:
        categories = set()
        for config in config_store.values():
            if config.get("category"):
                categories.add(config["category"])
        return list(categories)
        
    except Exception as e:
        logger.error(f"Failed to get configuration categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration categories")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
