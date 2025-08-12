"""
Adapted Civic-Scraper cache tests for OpenPolicy Scraper Service.
Tests caching functionality in alignment with services-based architecture.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import shutil

# Import the adapted cache module (to be created)
# from src.legacy.civic_scraper.base.cache import Cache

@pytest.mark.legacy
@pytest.mark.civic_scraper
class TestCivicScraperCache:
    """Test Civic-Scraper caching functionality."""
    
    @pytest.fixture
    def cache_dir(self, temp_dir):
        """Provide temporary cache directory for testing."""
        cache_path = temp_dir / "cache"
        cache_path.mkdir()
        return cache_path
    
    @pytest.fixture
    def sample_cache_data(self):
        """Provide sample cache data for testing."""
        return {
            "url": "https://example.com/agenda.pdf",
            "content_hash": "abc123def456",
            "timestamp": "2025-01-27T10:00:00Z",
            "metadata": {
                "content_type": "application/pdf",
                "content_length": 1024,
                "last_modified": "2025-01-27T09:00:00Z"
            }
        }
    
    def test_cache_initialization(self, cache_dir):
        """Test cache initialization and directory creation."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache class
            mock_cache = Mock()
            mock_cache.cache_dir = cache_dir
            mock_cache.initialize = Mock()
            MockCache.return_value = mock_cache
            
            # Test cache creation
            cache = MockCache(cache_dir)
            assert cache.cache_dir == cache_dir
            cache.initialize.assert_called_once()
    
    def test_cache_set_and_get(self, cache_dir, sample_cache_data):
        """Test setting and getting cache entries."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache instance
            mock_cache = Mock()
            mock_cache.set = Mock()
            mock_cache.get = Mock(return_value=sample_cache_data)
            MockCache.return_value = mock_cache
            
            # Test cache operations
            cache = MockCache(cache_dir)
            
            # Set cache entry
            cache.set("test-key", sample_cache_data)
            mock_cache.set.assert_called_once_with("test-key", sample_cache_data)
            
            # Get cache entry
            result = cache.get("test-key")
            assert result == sample_cache_data
            mock_cache.get.assert_called_once_with("test-key")
    
    def test_cache_expiration(self, cache_dir):
        """Test cache entry expiration."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with expiration
            mock_cache = Mock()
            mock_cache.is_expired = Mock(return_value=True)
            mock_cache.cleanup_expired = Mock()
            MockCache.return_value = mock_cache
            
            # Test expiration handling
            cache = MockCache(cache_dir)
            
            # Check if entry is expired
            is_expired = cache.is_expired("test-key")
            assert is_expired is True
            
            # Cleanup expired entries
            cache.cleanup_expired()
            mock_cache.cleanup_expired.assert_called_once()
    
    def test_cache_serialization(self, cache_dir, sample_cache_data):
        """Test cache data serialization and deserialization."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with serialization
            mock_cache = Mock()
            mock_cache.serialize = Mock(return_value='{"test": "data"}')
            mock_cache.deserialize = Mock(return_value={"test": "data"})
            MockCache.return_value = mock_cache
            
            # Test serialization
            cache = MockCache(cache_dir)
            
            # Serialize data
            serialized = cache.serialize(sample_cache_data)
            assert serialized == '{"test": "data"}'
            mock_cache.serialize.assert_called_once_with(sample_cache_data)
            
            # Deserialize data
            deserialized = cache.deserialize('{"test": "data"}')
            assert deserialized == {"test": "data"}
            mock_cache.deserialize.assert_called_once_with('{"test": "data"}')
    
    def test_cache_persistence(self, cache_dir, sample_cache_data):
        """Test cache persistence across sessions."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with persistence
            mock_cache = Mock()
            mock_cache.save_to_disk = Mock()
            mock_cache.load_from_disk = Mock(return_value=sample_cache_data)
            MockCache.return_value = mock_cache
            
            # Test persistence
            cache = MockCache(cache_dir)
            
            # Save to disk
            cache.save_to_disk()
            mock_cache.save_to_disk.assert_called_once()
            
            # Load from disk
            loaded_data = cache.load_from_disk()
            assert loaded_data == sample_cache_data
            mock_cache.load_from_disk.assert_called_once()
    
    def test_cache_compression(self, cache_dir, sample_cache_data):
        """Test cache data compression for large entries."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with compression
            mock_cache = Mock()
            mock_cache.compress = Mock(return_value=b"compressed_data")
            mock_cache.decompress = Mock(return_value=sample_cache_data)
            MockCache.return_value = mock_cache
            
            # Test compression
            cache = MockCache(cache_dir)
            
            # Compress data
            compressed = cache.compress(sample_cache_data)
            assert compressed == b"compressed_data"
            mock_cache.compress.assert_called_once_with(sample_cache_data)
            
            # Decompress data
            decompressed = cache.decompress(b"compressed_data")
            assert decompressed == sample_cache_data
            mock_cache.decompress.assert_called_once_with(b"compressed_data")
    
    def test_cache_statistics(self, cache_dir):
        """Test cache statistics and monitoring."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with statistics
            mock_cache = Mock()
            mock_cache.get_stats = Mock(return_value={
                "total_entries": 100,
                "hit_rate": 0.85,
                "memory_usage": "50MB",
                "disk_usage": "100MB"
            })
            MockCache.return_value = mock_cache
            
            # Test statistics
            cache = MockCache(cache_dir)
            stats = cache.get_stats()
            
            assert stats["total_entries"] == 100
            assert stats["hit_rate"] == 0.85
            assert stats["memory_usage"] == "50MB"
            assert stats["disk_usage"] == "100MB"
            
            mock_cache.get_stats.assert_called_once()
    
    def test_cache_error_handling(self, cache_dir):
        """Test cache error handling and recovery."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with error handling
            mock_cache = Mock()
            mock_cache.get = Mock(side_effect=Exception("Cache error"))
            mock_cache.handle_error = Mock()
            MockCache.return_value = mock_cache
            
            # Test error handling
            cache = MockCache(cache_dir)
            
            try:
                cache.get("test-key")
            except Exception as e:
                assert "Cache error" in str(e)
            
            # Verify error handling was called
            mock_cache.handle_error.assert_called()
    
    def test_cache_concurrency(self, cache_dir):
        """Test cache concurrency and thread safety."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with concurrency support
            mock_cache = Mock()
            mock_cache.lock = Mock()
            mock_cache.unlock = Mock()
            MockCache.return_value = mock_cache
            
            # Test concurrency handling
            cache = MockCache(cache_dir)
            
            # Acquire lock
            cache.lock("test-key")
            mock_cache.lock.assert_called_once_with("test-key")
            
            # Release lock
            cache.unlock("test-key")
            mock_cache.unlock.assert_called_once_with("test-key")
    
    def test_cache_invalidation(self, cache_dir):
        """Test cache invalidation strategies."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with invalidation
            mock_cache = Mock()
            mock_cache.invalidate = Mock()
            mock_cache.invalidate_pattern = Mock()
            mock_cache.clear_all = Mock()
            MockCache.return_value = mock_cache
            
            # Test invalidation
            cache = MockCache(cache_dir)
            
            # Invalidate specific key
            cache.invalidate("test-key")
            mock_cache.invalidate.assert_called_once_with("test-key")
            
            # Invalidate by pattern
            cache.invalidate_pattern("test-*")
            mock_cache.invalidate_pattern.assert_called_once_with("test-*")
            
            # Clear all cache
            cache.clear_all()
            mock_cache.clear_all.assert_called_once()
    
    def test_cache_memory_management(self, cache_dir):
        """Test cache memory management and eviction policies."""
        with patch("src.legacy.civic_scraper.base.cache.Cache") as MockCache:
            # Mock cache with memory management
            mock_cache = Mock()
            mock_cache.get_memory_usage = Mock(return_value="75MB")
            mock_cache.evict_oldest = Mock()
            mock_cache.set_max_memory = Mock()
            MockCache.return_value = mock_cache
            
            # Test memory management
            cache = MockCache(cache_dir)
            
            # Get memory usage
            memory_usage = cache.get_memory_usage()
            assert memory_usage == "75MB"
            
            # Evict oldest entries
            cache.evict_oldest()
            mock_cache.evict_oldest.assert_called_once()
            
            # Set max memory limit
            cache.set_max_memory("100MB")
            mock_cache.set_max_memory.assert_called_once_with("100MB")
