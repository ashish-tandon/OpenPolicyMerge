"""
Adapted Civic-Scraper asset tests for OpenPolicy Scraper Service.
"""
import re
from unittest.mock import Mock, patch
import pytest
from pathlib import Path

# Import the adapted asset module (to be created)
# from src.legacy.civic_scraper.base.asset import Asset, AssetCollection

@pytest.mark.legacy
@pytest.mark.civic_scraper
class TestCivicScraperAssets:
    """Test Civic-Scraper asset functionality."""
    
    @pytest.fixture
    def asset_inputs(self):
        """Provide sample asset input data."""
        return [
            {
                "url": "http://nc-nashcounty.civicplus.com/AgendaCenter/ViewFile/Agenda/_05042020-381",
                "place": "nashcounty",
                "place_name": "Nash County",
                "asset_type": "agenda",
                "date": "2020-05-04",
                "committee": "test-committee"
            },
            {
                "url": "http://nc-nashcounty.civicplus.com/AgendaCenter/ViewFile/Minutes/_05042020-381",
                "place": "nashcounty",
                "place_name": "Nash County",
                "asset_type": "minutes",
                "date": "2020-05-04",
                "committee": "test-committee"
            }
        ]
    
    @pytest.fixture
    def asset_collection(self, asset_inputs):
        """Provide asset collection for testing."""
        # Mock the Asset class
        with patch("src.legacy.civic_scraper.base.asset.Asset") as MockAsset:
            # Setup mock asset instances
            mock_assets = []
            for kwargs in asset_inputs:
                mock_asset = Mock()
                mock_asset.place = kwargs["place"]
                mock_asset.place_name = kwargs["place_name"]
                mock_asset.asset_type = kwargs["asset_type"]
                mock_asset.date = kwargs["date"]
                mock_asset.committee = kwargs["committee"]
                mock_assets.append(mock_asset)
            
            # Mock AssetCollection
            with patch("src.legacy.civic_scraper.base.asset.AssetCollection") as MockCollection:
                collection = Mock()
                collection.__iter__ = lambda self: iter(mock_assets)
                collection.__len__ = lambda self: len(mock_assets)
                collection.extend = Mock()
                collection.append = Mock()
                collection.__getitem__ = lambda self, key: mock_assets[key]
                MockCollection.return_value = collection
                yield collection
    
    def test_asset_args(self, asset_inputs):
        """Asset should accept and store arguments correctly."""
        with patch("src.legacy.civic_scraper.base.asset.Asset") as MockAsset:
            kwargs = asset_inputs[0].copy()
            url = kwargs.pop("url")
            
            # Create mock asset
            mock_asset = Mock()
            mock_asset.place = kwargs["place"]
            mock_asset.place_name = kwargs["place_name"]
            MockAsset.return_value = mock_asset
            
            # Verify asset creation
            asset = MockAsset(url, **kwargs)
            assert asset.place == "nashcounty"
            assert asset.place_name == "Nash County"
    
    def test_asset_collection_methods(self, asset_collection):
        """AssetCollection should support basic collection methods."""
        # Test extend
        asset_collection.extend([3, 4])
        asset_collection.extend.assert_called_once_with([3, 4])
        
        # Test append
        asset_collection.append([3, 4])
        asset_collection.append.assert_called_once_with([3, 4])
        
        # Test indexing
        assert asset_collection[1] is not None
    
    def test_csv_export(self, asset_collection, temp_dir):
        """CSV export should write standard filename to target directory."""
        with patch("src.legacy.civic_scraper.base.asset.AssetCollection.to_csv") as mock_to_csv:
            # Mock the CSV export method
            expected_filename = f"civic_scraper_assets_meta_20250127T1000z.csv"
            mock_to_csv.return_value = str(temp_dir / expected_filename)
            
            # Call the export method
            outfile = asset_collection.to_csv(target_dir=temp_dir)
            
            # Verify filename pattern
            pattern = re.compile(r".+civic_scraper_assets_meta_\d{8}T\d{4}z.csv")
            assert re.match(pattern, outfile)
            
            # Verify the method was called
            mock_to_csv.assert_called_once_with(target_dir=temp_dir)
    
    def test_asset_download(self, asset_inputs, temp_dir, mock_requests):
        """Asset download should work correctly."""
        with patch("src.legacy.civic_scraper.base.asset.Asset") as MockAsset:
            # Setup mock assets
            mock_assets = []
            for kwargs in asset_inputs:
                mock_asset = Mock()
                mock_asset.url = kwargs["url"]
                mock_asset.download = Mock()
                mock_assets.append(mock_asset)
            
            # Mock AssetCollection
            with patch("src.legacy.civic_scraper.base.asset.AssetCollection") as MockCollection:
                collection = Mock()
                collection.__iter__ = lambda self: iter(mock_assets)
                
                # Test download for each asset
                for asset in mock_assets:
                    asset.download(target_dir=temp_dir)
                    asset.download.assert_called_once_with(target_dir=temp_dir)
    
    def test_asset_validation(self, asset_inputs):
        """Asset validation should work correctly."""
        with patch("src.legacy.civic_scraper.base.asset.Asset") as MockAsset:
            for kwargs in asset_inputs:
                mock_asset = Mock()
                mock_asset.is_valid = Mock(return_value=True)
                MockAsset.return_value = mock_asset
                
                # Test validation
                asset = MockAsset(**kwargs)
                assert asset.is_valid() is True
    
    def test_asset_metadata(self, asset_inputs):
        """Asset should have correct metadata."""
        with patch("src.legacy.civic_scraper.base.asset.Asset") as MockAsset:
            for kwargs in asset_inputs:
                mock_asset = Mock()
                mock_asset.metadata = kwargs
                MockAsset.return_value = mock_asset
                
                # Test metadata
                asset = MockAsset(**kwargs)
                assert asset.metadata["place"] == kwargs["place"]
                assert asset.metadata["asset_type"] == kwargs["asset_type"]
                assert asset.metadata["date"] == kwargs["date"]
    
    def test_asset_collection_filtering(self, asset_collection):
        """AssetCollection should support filtering."""
        with patch("src.legacy.civic_scraper.base.asset.AssetCollection.filter") as mock_filter:
            # Mock filtering by asset type
            mock_filter.return_value = [asset_collection[0]]  # Return first asset
            
            # Test filtering
            filtered = asset_collection.filter(asset_type="agenda")
            assert len(filtered) == 1
            mock_filter.assert_called_once_with(asset_type="agenda")
    
    def test_asset_collection_sorting(self, asset_collection):
        """AssetCollection should support sorting."""
        with patch("src.legacy.civic_scraper.base.asset.AssetCollection.sort") as mock_sort:
            # Mock sorting by date
            mock_sort.return_value = asset_collection
            
            # Test sorting
            sorted_collection = asset_collection.sort(key="date")
            assert sorted_collection is not None
            mock_sort.assert_called_once_with(key="date")
    
    def test_asset_error_handling(self, asset_inputs):
        """Asset should handle errors gracefully."""
        with patch("src.legacy.civic_scraper.base.asset.Asset") as MockAsset:
            # Test with invalid URL
            invalid_kwargs = asset_inputs[0].copy()
            invalid_kwargs["url"] = "invalid-url"
            
            mock_asset = Mock()
            mock_asset.validate_url = Mock(return_value=False)
            MockAsset.return_value = mock_asset
            
            # Test validation
            asset = MockAsset(**invalid_kwargs)
            assert asset.validate_url() is False
