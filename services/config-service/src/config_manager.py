import logging
import json
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from sqlalchemy import text
from .database import get_session
import uuid
import asyncio

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management for OpenPolicy platform"""
    
    def __init__(self, default_config_path: str = "/app/config/defaults.yaml"):
        self.default_config_path = default_config_path
        self.config_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = None
        
        # Load default configurations
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default configurations from file"""
        try:
            # Default configurations for all services
            self.default_configs = {
                "policy": {
                    "evaluation_timeout": 30,
                    "max_concurrent_evaluations": 100,
                    "cache_enabled": True,
                    "cache_ttl": 300,
                    "default_mode": "strict",
                    "opa_url": "http://opa-service:8181",
                    "retry_attempts": 3
                },
                "search": {
                    "max_results": 100,
                    "default_limit": 50,
                    "suggestion_limit": 10,
                    "indexing_batch_size": 1000,
                    "relevance_threshold": 0.1
                },
                "auth": {
                    "jwt_secret": os.getenv("JWT_SECRET", "default-secret"),
                    "jwt_algorithm": "HS256",
                    "access_token_expire_minutes": 30,
                    "refresh_token_expire_days": 7,
                    "password_min_length": 8,
                    "max_login_attempts": 5,
                    "lockout_duration_minutes": 15
                },
                "notification": {
                    "default_channels": ["in_app"],
                    "email_enabled": True,
                    "push_enabled": True,
                    "sms_enabled": False,
                    "max_retries": 3,
                    "retry_delay_seconds": 5
                },
                "monitoring": {
                    "metrics_enabled": True,
                    "health_check_interval": 60,
                    "alerting_enabled": True,
                    "retention_days": 30,
                    "sampling_rate": 1.0
                },
                "database": {
                    "connection_pool_size": 10,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                    "pool_recycle": 3600,
                    "echo": False
                },
                "api": {
                    "rate_limit_enabled": True,
                    "rate_limit_requests": 100,
                    "rate_limit_window": 60,
                    "cors_origins": ["*"],
                    "max_request_size": "10MB"
                },
                "logging": {
                    "level": "INFO",
                    "format": "json",
                    "output": "stdout",
                    "rotation": "daily",
                    "retention": "30 days"
                }
            }
            
            logger.info("Default configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load default configurations: {e}")
            self.default_configs = {}
    
    async def get_config(self, key: str, service: str = None, 
                        environment: str = None, user_id: str = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            service: Service name (optional)
            environment: Environment (dev, staging, prod)
            user_id: User ID for user-specific configs
        
        Returns:
            Configuration value
        """
        try:
            # Check cache first
            cache_key = f"{service}:{environment}:{user_id}:{key}"
            if self._is_cache_valid():
                cached_value = self.config_cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
            
            # Get from database
            config_value = await self._get_config_from_db(key, service, environment, user_id)
            
            # Fallback to defaults
            if config_value is None:
                config_value = self._get_default_config(key, service)
            
            # Cache the result
            self.config_cache[cache_key] = config_value
            
            return config_value
            
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return self._get_default_config(key, service)
    
    async def set_config(self, key: str, value: Any, service: str = None,
                        environment: str = None, user_id: str = None, 
                        description: str = None) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
            service: Service name
            environment: Environment
            user_id: User ID for user-specific configs
            description: Configuration description
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session = get_session()
            
            # Check if config exists
            existing = session.execute(
                text("""
                    SELECT id FROM config.configurations 
                    WHERE config_key = :key AND service = :service 
                    AND environment = :environment AND user_id = :user_id
                """),
                {
                    "key": key,
                    "service": service,
                    "environment": environment,
                    "user_id": user_id
                }
            ).fetchone()
            
            if existing:
                # Update existing config
                session.execute(
                    text("""
                        UPDATE config.configurations 
                        SET config_value = :value, description = :description,
                            updated_at = NOW(), updated_by = :updated_by
                        WHERE id = :id
                    """),
                    {
                        "value": json.dumps(value),
                        "description": description,
                        "updated_by": user_id or "system",
                        "id": existing[0]
                    }
                )
            else:
                # Create new config
                session.execute(
                    text("""
                        INSERT INTO config.configurations 
                        (id, config_key, config_value, service, environment, user_id,
                         description, created_at, updated_at, created_by, updated_by)
                        VALUES (:id, :key, :value, :service, :environment, :user_id,
                               :description, NOW(), NOW(), :created_by, :updated_by)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "key": key,
                        "value": json.dumps(value),
                        "service": service,
                        "environment": environment,
                        "user_id": user_id,
                        "description": description,
                        "created_by": user_id or "system",
                        "updated_by": user_id or "system"
                    }
                )
            
            session.commit()
            
            # Clear cache
            self._clear_cache()
            
            # Log configuration change
            await self._log_config_change(key, value, service, environment, user_id, "set")
            
            logger.info(f"Configuration {key} set successfully for service {service}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    async def delete_config(self, key: str, service: str = None,
                          environment: str = None, user_id: str = None) -> bool:
        """
        Delete configuration
        
        Args:
            key: Configuration key
            service: Service name
            environment: Environment
            user_id: User ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session = get_session()
            
            result = session.execute(
                text("""
                    DELETE FROM config.configurations 
                    WHERE config_key = :key AND service = :service 
                    AND environment = :environment AND user_id = :user_id
                """),
                {
                    "key": key,
                    "service": service,
                    "environment": environment,
                    "user_id": user_id
                }
            )
            
            session.commit()
            
            if result.rowcount > 0:
                # Clear cache
                self._clear_cache()
                
                # Log configuration change
                await self._log_config_change(key, None, service, environment, user_id, "delete")
                
                logger.info(f"Configuration {key} deleted successfully")
                return True
            else:
                logger.warning(f"Configuration {key} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete config {key}: {e}")
            return False
    
    async def get_service_configs(self, service: str, environment: str = None,
                                 user_id: str = None) -> Dict[str, Any]:
        """
        Get all configurations for a service
        
        Args:
            service: Service name
            environment: Environment
            user_id: User ID
        
        Returns:
            Dictionary of all service configurations
        """
        try:
            session = get_session()
            
            query = """
                SELECT config_key, config_value, description, created_at, updated_at
                FROM config.configurations 
                WHERE service = :service
            """
            params = {"service": service}
            
            if environment:
                query += " AND environment = :environment"
                params["environment"] = environment
            
            if user_id:
                query += " AND user_id = :user_id"
                params["user_id"] = user_id
            
            query += " ORDER BY config_key"
            
            result = session.execute(text(query), params).fetchall()
            
            configs = {}
            for row in result:
                config_data = dict(row)
                try:
                    configs[config_data["config_key"]] = {
                        "value": json.loads(config_data["config_value"]),
                        "description": config_data["description"],
                        "created_at": config_data["created_at"].isoformat() if config_data["created_at"] else None,
                        "updated_at": config_data["updated_at"].isoformat() if config_data["updated_at"] else None
                    }
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in config value for {config_data['config_key']}")
                    configs[config_data["config_key"]] = {
                        "value": config_data["config_value"],
                        "description": config_data["description"],
                        "created_at": config_data["created_at"].isoformat() if config_data["created_at"] else None,
                        "updated_at": config_data["updated_at"].isoformat() if config_data["updated_at"] else None
                    }
            
            # Merge with defaults
            if service in self.default_configs:
                for key, value in self.default_configs[service].items():
                    if key not in configs:
                        configs[key] = {
                            "value": value,
                            "description": f"Default {key} configuration",
                            "created_at": None,
                            "updated_at": None
                        }
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to get service configs for {service}: {e}")
            return self.default_configs.get(service, {})
    
    async def get_config_history(self, key: str, service: str = None,
                                environment: str = None, user_id: str = None,
                                limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get configuration change history
        
        Args:
            key: Configuration key
            service: Service name
            environment: Environment
            user_id: User ID
            limit: Maximum number of history entries
        
        Returns:
            List of configuration changes
        """
        try:
            session = get_session()
            
            query = """
                SELECT ch.config_key, ch.old_value, ch.new_value, ch.change_type,
                       ch.changed_at, ch.changed_by, ch.reason
                FROM config.config_history ch
                JOIN config.configurations c ON ch.configuration_id = c.id
                WHERE ch.config_key = :key
            """
            params = {"key": key}
            
            if service:
                query += " AND c.service = :service"
                params["service"] = service
            
            if environment:
                query += " AND c.environment = :environment"
                params["environment"] = environment
            
            if user_id:
                query += " AND c.user_id = :user_id"
                params["user_id"] = user_id
            
            query += " ORDER BY ch.changed_at DESC LIMIT :limit"
            params["limit"] = limit
            
            result = session.execute(text(query), params).fetchall()
            
            history = []
            for row in result:
                history_entry = dict(row)
                try:
                    history_entry["old_value"] = json.loads(history_entry["old_value"]) if history_entry["old_value"] else None
                    history_entry["new_value"] = json.loads(history_entry["new_value"]) if history_entry["new_value"] else None
                except json.JSONDecodeError:
                    pass
                
                history_entry["changed_at"] = history_entry["changed_at"].isoformat() if history_entry["changed_at"] else None
                history.append(history_entry)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get config history for {key}: {e}")
            return []
    
    async def validate_config(self, key: str, value: Any, service: str = None) -> Dict[str, Any]:
        """
        Validate configuration value
        
        Args:
            key: Configuration key
            value: Configuration value to validate
            service: Service name
        
        Returns:
            Validation result
        """
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Get validation rules for the key
            validation_rules = self._get_validation_rules(key, service)
            
            if not validation_rules:
                return validation_result
            
            # Type validation
            if "type" in validation_rules:
                expected_type = validation_rules["type"]
                if not isinstance(value, expected_type):
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Expected type {expected_type}, got {type(value)}")
            
            # Range validation
            if "min" in validation_rules and isinstance(value, (int, float)):
                if value < validation_rules["min"]:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Value {value} is below minimum {validation_rules['min']}")
            
            if "max" in validation_rules and isinstance(value, (int, float)):
                if value > validation_rules["max"]:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Value {value} is above maximum {validation_rules['max']}")
            
            # Enum validation
            if "enum" in validation_rules:
                if value not in validation_rules["enum"]:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Value {value} is not in allowed values {validation_rules['enum']}")
            
            # Pattern validation for strings
            if "pattern" in validation_rules and isinstance(value, str):
                import re
                if not re.match(validation_rules["pattern"], value):
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Value does not match pattern {validation_rules['pattern']}")
            
            # Custom validation function
            if "custom_validator" in validation_rules:
                try:
                    custom_result = validation_rules["custom_validator"](value)
                    if not custom_result["valid"]:
                        validation_result["valid"] = False
                        validation_result["errors"].extend(custom_result.get("errors", []))
                except Exception as e:
                    validation_result["warnings"].append(f"Custom validation failed: {e}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Config validation failed for {key}: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {e}"],
                "warnings": []
            }
    
    def _get_validation_rules(self, key: str, service: str = None) -> Dict[str, Any]:
        """Get validation rules for configuration key"""
        # Define validation rules for common configuration keys
        validation_rules = {
            "evaluation_timeout": {
                "type": int,
                "min": 1,
                "max": 300
            },
            "max_concurrent_evaluations": {
                "type": int,
                "min": 1,
                "max": 1000
            },
            "cache_ttl": {
                "type": int,
                "min": 0,
                "max": 86400
            },
            "jwt_algorithm": {
                "type": str,
                "enum": ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
            },
            "access_token_expire_minutes": {
                "type": int,
                "min": 1,
                "max": 1440
            },
            "password_min_length": {
                "type": int,
                "min": 6,
                "max": 128
            },
            "max_results": {
                "type": int,
                "min": 1,
                "max": 10000
            },
            "rate_limit_requests": {
                "type": int,
                "min": 1,
                "max": 10000
            }
        }
        
        return validation_rules.get(key, {})
    
    def _get_default_config(self, key: str, service: str = None) -> Any:
        """Get default configuration value"""
        if service and service in self.default_configs:
            return self.default_configs[service].get(key)
        return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.last_cache_update:
            return False
        
        return (datetime.now() - self.last_cache_update).total_seconds() < self.cache_ttl
    
    def _clear_cache(self):
        """Clear configuration cache"""
        self.config_cache.clear()
        self.last_cache_update = None
    
    async def _get_config_from_db(self, key: str, service: str = None,
                                 environment: str = None, user_id: str = None) -> Any:
        """Get configuration value from database"""
        try:
            session = get_session()
            
            query = """
                SELECT config_value FROM config.configurations 
                WHERE config_key = :key
            """
            params = {"key": key}
            
            if service:
                query += " AND service = :service"
                params["service"] = service
            
            if environment:
                query += " AND environment = :environment"
                params["environment"] = environment
            
            if user_id:
                query += " AND user_id = :user_id"
                params["user_id"] = user_id
            
            result = session.execute(text(query), params).fetchone()
            
            if result:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in config value for {key}")
                    return result[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get config from database: {e}")
            return None
    
    async def _log_config_change(self, key: str, value: Any, service: str = None,
                                environment: str = None, user_id: str = None,
                                change_type: str = "set"):
        """Log configuration change"""
        try:
            session = get_session()
            
            # Get configuration ID
            config_query = """
                SELECT id FROM config.configurations 
                WHERE config_key = :key AND service = :service 
                AND environment = :environment AND user_id = :user_id
            """
            
            config_result = session.execute(
                text(config_query),
                {
                    "key": key,
                    "service": service,
                    "environment": environment,
                    "user_id": user_id
                }
            ).fetchone()
            
            if config_result:
                config_id = config_result[0]
                
                # Get old value
                old_value_result = session.execute(
                    text("SELECT config_value FROM config.configurations WHERE id = :id"),
                    {"id": config_id}
                ).fetchone()
                
                old_value = old_value_result[0] if old_value_result else None
                
                # Log the change
                session.execute(
                    text("""
                        INSERT INTO config.config_history 
                        (id, configuration_id, config_key, old_value, new_value,
                         change_type, changed_at, changed_by, reason)
                        VALUES (:id, :config_id, :key, :old_value, :new_value,
                               :change_type, NOW(), :changed_by, :reason)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "config_id": config_id,
                        "key": key,
                        "old_value": old_value,
                        "new_value": json.dumps(value) if value is not None else None,
                        "change_type": change_type,
                        "changed_by": user_id or "system",
                        "reason": f"Configuration {change_type} via API"
                    }
                )
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to log config change: {e}")
    
    async def refresh_cache(self):
        """Refresh configuration cache"""
        try:
            self._clear_cache()
            self.last_cache_update = datetime.now()
            logger.info("Configuration cache refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh config cache: {e}")
    
    async def export_configs(self, service: str = None, environment: str = None,
                            format: str = "json") -> str:
        """
        Export configurations
        
        Args:
            service: Service name
            environment: Environment
            format: Export format (json, yaml)
        
        Returns:
            Exported configurations
        """
        try:
            if service:
                configs = await self.get_service_configs(service, environment)
            else:
                # Export all configurations
                configs = {}
                for service_name in self.default_configs.keys():
                    service_configs = await self.get_service_configs(service_name, environment)
                    configs[service_name] = service_configs
            
            if format.lower() == "yaml":
                import yaml
                return yaml.dump(configs, default_flow_style=False)
            else:
                return json.dumps(configs, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to export configs: {e}")
            return "{}"
    
    async def import_configs(self, config_data: str, format: str = "json",
                            overwrite: bool = False) -> Dict[str, Any]:
        """
        Import configurations
        
        Args:
            config_data: Configuration data
            format: Import format (json, yaml)
            overwrite: Whether to overwrite existing configs
        
        Returns:
            Import results
        """
        try:
            if format.lower() == "yaml":
                import yaml
                configs = yaml.safe_load(config_data)
            else:
                configs = json.loads(config_data)
            
            results = {
                "total": 0,
                "imported": 0,
                "skipped": 0,
                "errors": []
            }
            
            for service, service_configs in configs.items():
                for key, config_info in service_configs.items():
                    results["total"] += 1
                    
                    try:
                        if isinstance(config_info, dict):
                            value = config_info.get("value", config_info)
                        else:
                            value = config_info
                        
                        # Check if config exists
                        existing = await self.get_config(key, service)
                        
                        if existing is not None and not overwrite:
                            results["skipped"] += 1
                            continue
                        
                        # Set the configuration
                        success = await self.set_config(
                            key, value, service, 
                            description=f"Imported from {format} file"
                        )
                        
                        if success:
                            results["imported"] += 1
                        else:
                            results["errors"].append(f"Failed to import {service}.{key}")
                    
                    except Exception as e:
                        results["errors"].append(f"Error importing {service}.{key}: {e}")
            
            logger.info(f"Configuration import completed: {results['imported']} imported, {results['skipped']} skipped")
            return results
            
        except Exception as e:
            logger.error(f"Failed to import configs: {e}")
            return {"total": 0, "imported": 0, "skipped": 0, "errors": [str(e)]}
