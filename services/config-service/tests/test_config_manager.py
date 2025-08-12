import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.config_manager import ConfigManager

@pytest.fixture
def config_manager():
    """Create config manager instance"""
    return ConfigManager()

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.execute = Mock()
    session.commit = Mock()
    return session

@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing"""
    return {
        "key": "test_key",
        "value": "test_value",
        "service": "test_service",
        "environment": "dev",
        "user_id": "user-123",
        "description": "Test configuration"
    }

class TestConfigManager:
    """Test cases for ConfigManager"""
    
    def test_initialization(self, config_manager):
        """Test ConfigManager initialization"""
        assert config_manager.default_configs is not None
        assert "policy" in config_manager.default_configs
        assert "search" in config_manager.default_configs
        assert "auth" in config_manager.default_configs
        assert config_manager.config_cache == {}
        assert config_manager.cache_ttl == 300
    
    def test_default_configs_loaded(self, config_manager):
        """Test that default configurations are properly loaded"""
        # Check policy service defaults
        policy_configs = config_manager.default_configs["policy"]
        assert policy_configs["evaluation_timeout"] == 30
        assert policy_configs["max_concurrent_evaluations"] == 100
        assert policy_configs["cache_enabled"] is True
        
        # Check search service defaults
        search_configs = config_manager.default_configs["search"]
        assert search_configs["max_results"] == 100
        assert search_configs["default_limit"] == 50
        
        # Check auth service defaults
        auth_configs = config_manager.default_configs["auth"]
        assert auth_configs["jwt_algorithm"] == "HS256"
        assert auth_configs["access_token_expire_minutes"] == 30

class TestConfigOperations:
    """Test cases for configuration operations"""
    
    @pytest.mark.asyncio
    async def test_get_config_from_cache(self, config_manager):
        """Test getting configuration from cache"""
        # Set up cache
        config_manager.config_cache["test:dev:user:key"] = "cached_value"
        config_manager.last_cache_update = datetime.now()
        
        # Mock database call
        with patch.object(config_manager, '_get_config_from_db') as mock_db:
            result = await config_manager.get_config("key", "test", "dev", "user")
            
            assert result == "cached_value"
            mock_db.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_config_from_database(self, config_manager):
        """Test getting configuration from database"""
        # Clear cache
        config_manager.config_cache.clear()
        config_manager.last_cache_update = None
        
        with patch.object(config_manager, '_get_config_from_db') as mock_db:
            mock_db.return_value = "db_value"
            
            result = await config_manager.get_config("key", "test", "dev", "user")
            
            assert result == "db_value"
            mock_db.assert_called_once_with("key", "test", "dev", "user")
    
    @pytest.mark.asyncio
    async def test_get_config_fallback_to_default(self, config_manager):
        """Test getting configuration falls back to default"""
        # Clear cache
        config_manager.config_cache.clear()
        config_manager.last_cache_update = None
        
        with patch.object(config_manager, '_get_config_from_db') as mock_db:
            mock_db.return_value = None
            
            result = await config_manager.get_config("evaluation_timeout", "policy")
            
            assert result == 30  # Default value from policy configs
            mock_db.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_config_database_error(self, config_manager):
        """Test getting configuration with database error"""
        # Clear cache
        config_manager.config_cache.clear()
        config_manager.last_cache_update = None
        
        with patch.object(config_manager, '_get_config_from_db') as mock_db:
            mock_db.side_effect = Exception("Database error")
            
            result = await config_manager.get_config("evaluation_timeout", "policy")
            
            assert result == 30  # Should fall back to default
            mock_db.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_config_new(self, config_manager, sample_config_data):
        """Test setting new configuration"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.return_value.fetchone.return_value = None
            mock_get_session.return_value = mock_session
            
            with patch.object(config_manager, '_log_config_change') as mock_log:
                result = await config_manager.set_config(
                    sample_config_data["key"],
                    sample_config_data["value"],
                    sample_config_data["service"],
                    sample_config_data["environment"],
                    sample_config_data["user_id"],
                    sample_config_data["description"]
                )
                
                assert result is True
                assert mock_session.execute.call_count == 1
                assert mock_session.commit.call_count == 1
                mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_config_existing(self, config_manager, sample_config_data):
        """Test updating existing configuration"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.return_value.fetchone.return_value = ["existing_id"]
            mock_get_session.return_value = mock_session
            
            with patch.object(config_manager, '_log_config_change') as mock_log:
                result = await config_manager.set_config(
                    sample_config_data["key"],
                    "updated_value",
                    sample_config_data["service"],
                    sample_config_data["environment"],
                    sample_config_data["user_id"],
                    "Updated description"
                )
                
                assert result is True
                assert mock_session.execute.call_count == 1
                assert mock_session.commit.call_count == 1
                mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_config_database_error(self, config_manager, sample_config_data):
        """Test setting configuration with database error"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.side_effect = Exception("Database error")
            mock_get_session.return_value = mock_session
            
            result = await config_manager.set_config(
                sample_config_data["key"],
                sample_config_data["value"],
                sample_config_data["service"]
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_config_success(self, config_manager):
        """Test successful configuration deletion"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_result = Mock()
            mock_result.rowcount = 1
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            with patch.object(config_manager, '_log_config_change') as mock_log:
                result = await config_manager.delete_config("test_key", "test_service")
                
                assert result is True
                assert mock_session.commit.call_count == 1
                mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_config_not_found(self, config_manager):
        """Test deleting non-existent configuration"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_result = Mock()
            mock_result.rowcount = 0
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await config_manager.delete_config("non_existent", "test_service")
            
            assert result is False

class TestServiceConfigs:
    """Test cases for service configuration operations"""
    
    @pytest.mark.asyncio
    async def test_get_service_configs_success(self, config_manager):
        """Test successful retrieval of service configurations"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    config_key="timeout",
                    config_value='"30"',
                    description="Timeout value",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                Mock(
                    config_key="max_connections",
                    config_value='"100"',
                    description="Max connections",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await config_manager.get_service_configs("test_service")
            
            assert "timeout" in result
            assert "max_connections" in result
            assert result["timeout"]["value"] == "30"
            assert result["max_connections"]["value"] == "100"
    
    @pytest.mark.asyncio
    async def test_get_service_configs_with_defaults(self, config_manager):
        """Test service configs merged with defaults"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_result = Mock()
            mock_result.fetchall.return_value = []
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await config_manager.get_service_configs("policy")
            
            # Should include defaults
            assert "evaluation_timeout" in result
            assert result["evaluation_timeout"]["value"] == 30
            assert "default" in result["evaluation_timeout"]["description"]
    
    @pytest.mark.asyncio
    async def test_get_service_configs_invalid_json(self, config_manager):
        """Test service configs with invalid JSON"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    config_key="invalid_json",
                    config_value="invalid json string",
                    description="Invalid JSON",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await config_manager.get_service_configs("test_service")
            
            assert "invalid_json" in result
            assert result["invalid_json"]["value"] == "invalid json string"

class TestConfigHistory:
    """Test cases for configuration history"""
    
    @pytest.mark.asyncio
    async def test_get_config_history_success(self, config_manager):
        """Test successful retrieval of configuration history"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    config_key="test_key",
                    old_value='"old_value"',
                    new_value='"new_value"',
                    change_type="set",
                    changed_at=datetime.now(),
                    changed_by="user-123",
                    reason="Configuration update"
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await config_manager.get_config_history("test_key")
            
            assert len(result) == 1
            assert result[0]["config_key"] == "test_key"
            assert result[0]["old_value"] == "old_value"
            assert result[0]["new_value"] == "new_value"
            assert result[0]["change_type"] == "set"
    
    @pytest.mark.asyncio
    async def test_get_config_history_invalid_json(self, config_manager):
        """Test config history with invalid JSON values"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    config_key="test_key",
                    old_value="invalid json",
                    new_value='"valid_json"',
                    change_type="set",
                    changed_at=datetime.now(),
                    changed_by="user-123",
                    reason="Configuration update"
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await config_manager.get_config_history("test_key")
            
            assert len(result) == 1
            assert result[0]["old_value"] == "invalid json"
            assert result[0]["new_value"] == "valid_json"

class TestConfigValidation:
    """Test cases for configuration validation"""
    
    def test_validate_config_success(self, config_manager):
        """Test successful configuration validation"""
        result = config_manager.validate_config("evaluation_timeout", 30, "policy")
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_validate_config_type_error(self, config_manager):
        """Test configuration validation with type error"""
        result = config_manager.validate_config("evaluation_timeout", "invalid", "policy")
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "Expected type" in result["errors"][0]
    
    def test_validate_config_range_error(self, config_manager):
        """Test configuration validation with range error"""
        result = config_manager.validate_config("evaluation_timeout", 500, "policy")
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "above maximum" in result["errors"][0]
    
    def test_validate_config_enum_error(self, config_manager):
        """Test configuration validation with enum error"""
        result = config_manager.validate_config("jwt_algorithm", "INVALID", "auth")
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "not in allowed values" in result["errors"][0]
    
    def test_validate_config_pattern_error(self, config_manager):
        """Test configuration validation with pattern error"""
        # Add a pattern validation rule for testing
        config_manager._get_validation_rules = lambda key, service: {
            "test_pattern": {"pattern": r"^\d+$"}
        }
        
        result = config_manager.validate_config("test_pattern", "abc", "test")
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "does not match pattern" in result["errors"][0]

class TestConfigImportExport:
    """Test cases for configuration import/export"""
    
    def test_export_configs_json(self, config_manager):
        """Test configuration export in JSON format"""
        result = config_manager.export_configs("policy", "dev", "json")
        
        # Should return valid JSON
        parsed = json.loads(result)
        assert "policy" in parsed
        assert "evaluation_timeout" in parsed["policy"]
    
    def test_export_configs_yaml(self, config_manager):
        """Test configuration export in YAML format"""
        try:
            import yaml
            result = config_manager.export_configs("policy", "dev", "yaml")
            
            # Should return valid YAML
            parsed = yaml.safe_load(result)
            assert "policy" in parsed
            assert "evaluation_timeout" in parsed["policy"]
        except ImportError:
            pytest.skip("PyYAML not available")
    
    @pytest.mark.asyncio
    async def test_import_configs_success(self, config_manager):
        """Test successful configuration import"""
        config_data = {
            "test_service": {
                "test_key": "test_value"
            }
        }
        
        with patch.object(config_manager, 'set_config') as mock_set:
            mock_set.return_value = True
            
            result = await config_manager.import_configs(
                json.dumps(config_data),
                "json"
            )
            
            assert result["total"] == 1
            assert result["imported"] == 1
            assert result["failed"] == 0
            assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_import_configs_partial_failure(self, config_manager):
        """Test configuration import with partial failures"""
        config_data = {
            "test_service": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        
        with patch.object(config_manager, 'set_config') as mock_set:
            mock_set.side_effect = [True, False]
            
            result = await config_manager.import_configs(
                json.dumps(config_data),
                "json"
            )
            
            assert result["total"] == 2
            assert result["imported"] == 1
            assert result["failed"] == 1
            assert len(result["errors"]) == 1

class TestCacheManagement:
    """Test cases for cache management"""
    
    def test_cache_validity_check(self, config_manager):
        """Test cache validity checking"""
        # Cache should be invalid initially
        assert config_manager.is_cache_valid() is False
        
        # Set cache update time
        config_manager.last_cache_update = datetime.now()
        assert config_manager.is_cache_valid() is True
        
        # Set cache update time to old
        config_manager.last_cache_update = datetime.now() - timedelta(seconds=400)
        assert config_manager.is_cache_valid() is False
    
    def test_cache_clearing(self, config_manager):
        """Test cache clearing"""
        # Add some data to cache
        config_manager.config_cache["test"] = "value"
        config_manager.last_cache_update = datetime.now()
        
        # Clear cache
        config_manager._clear_cache()
        
        assert config_manager.config_cache == {}
        assert config_manager.last_cache_update is None
    
    @pytest.mark.asyncio
    async def test_cache_refresh(self, config_manager):
        """Test cache refresh"""
        config_manager.last_cache_update = None
        
        await config_manager.refresh_cache()
        
        assert config_manager.is_cache_valid() is True
        assert config_manager.config_cache == {}

class TestErrorHandling:
    """Test cases for error handling"""
    
    @pytest.mark.asyncio
    async def test_get_config_database_error_handling(self, config_manager):
        """Test error handling in get_config_from_db"""
        with patch('src.config_manager.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.side_effect = Exception("Database connection failed")
            mock_get_session.return_value = mock_session
            
            result = await config_manager._get_config_from_db("test_key", "test_service")
            
            assert result is None
    
    def test_validation_error_handling(self, config_manager):
        """Test error handling in config validation"""
        # Test with custom validator that raises exception
        validation_rules = {
            "test_key": {
                "custom_validator": lambda x: {"valid": False, "errors": ["Custom error"]}
            }
        }
        
        config_manager._get_validation_rules = lambda key, service: validation_rules.get(key, {})
        
        result = config_manager.validate_config("test_key", "test_value", "test_service")
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0] == "Custom error"

if __name__ == "__main__":
    pytest.main([__file__])
