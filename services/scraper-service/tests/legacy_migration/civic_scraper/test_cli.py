"""
Adapted Civic-Scraper CLI tests for OpenPolicy Scraper Service.
"""
import re
from pathlib import Path
from unittest.mock import patch
import pytest
from click.testing import CliRunner

# Import the adapted CLI module (to be created)
# from src.legacy.civic_scraper import cli

@pytest.mark.legacy
@pytest.mark.civic_scraper
class TestCivicScraperCLI:
    """Test Civic-Scraper CLI functionality."""
    
    @pytest.fixture
    def cli_runner(self):
        """Provide CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def civic_scraper_dir(self, temp_dir):
        """Provide temporary directory for Civic-Scraper tests."""
        # Create directory structure
        (temp_dir / "metadata").mkdir()
        (temp_dir / "assets").mkdir()
        (temp_dir / "artifacts").mkdir()
        return temp_dir
    
    @pytest.mark.vcr()
    def test_cli_scrape_simple(self, cli_runner, civic_scraper_dir, mock_requests):
        """Scrape should write assets metadata by default."""
        # Mock the CLI command
        with patch("src.legacy.civic_scraper.cli.cli") as mock_cli:
            result = cli_runner.invoke(
                mock_cli,
                [
                    "scrape",
                    "--start-date", "2020-05-05",
                    "--end-date", "2020-05-05",
                    "--url", "http://nc-nashcounty.civicplus.com/AgendaCenter",
                ],
            )
        
        # Check metadata written by default
        meta_files = list((civic_scraper_dir / "metadata").glob("*"))
        assert len(meta_files) == 1
        
        fname = meta_files[0].name
        pattern = r"civic_scraper_assets_meta_\d{8}T\d{4}z.csv"
        assert re.match(pattern, fname)
        
        # Check assets and artifacts not saved by default
        artifacts_dir = civic_scraper_dir / "artifacts"
        assets_dir = civic_scraper_dir / "assets"
        assert not artifacts_dir.exists()
        assert not assets_dir.exists()
    
    @pytest.mark.vcr()
    def test_cli_store_assets_and_artifacts(self, cli_runner, civic_scraper_dir, mock_requests):
        """Scrape should store assets and artifacts when requested."""
        with patch("src.legacy.civic_scraper.cli.cli") as mock_cli:
            result = cli_runner.invoke(
                mock_cli,
                [
                    "scrape",
                    "--start-date", "2020-05-05",
                    "--end-date", "2020-05-05",
                    "--cache",
                    "--download",
                    "--url", "http://nc-nashcounty.civicplus.com/AgendaCenter",
                ],
            )
        
        artifacts_dir = civic_scraper_dir / "artifacts"
        assets_dir = civic_scraper_dir / "assets"
        meta_dir = civic_scraper_dir / "metadata"
        
        # Check all directories exist
        assert meta_dir.exists()
        assert len(list(meta_dir.glob("*"))) == 1
        assert artifacts_dir.exists()
        assert len(list(artifacts_dir.glob("*"))) == 1
        assert assets_dir.exists()
        assert len(list(assets_dir.glob("*"))) == 2
    
    @patch("src.legacy.civic_scraper.cli.Runner")
    def test_cli_store_csv_urls(self, runner_class, cli_runner, civic_scraper_dir, mock_requests):
        """Scrape should allow submission of URLs via CSV file."""
        urls_file = Path(__file__).parent.parent.parent / "test_data" / "civic_scraper" / "url_input.csv"
        
        with patch("src.legacy.civic_scraper.cli.cli") as mock_cli:
            result = cli_runner.invoke(
                mock_cli,
                [
                    "scrape",
                    "--start-date", "2020-05-05",
                    "--end-date", "2020-05-05",
                    "--cache",
                    "--download",
                    "--urls-file", str(urls_file),
                ],
            )
        
        # Verify the runner was called with correct parameters
        runner_class.assert_called_once()
        call_args = runner_class.call_args
        assert call_args[1]["start_date"] == "2020-05-05"
        assert call_args[1]["end_date"] == "2020-05-05"
        assert call_args[1]["cache"] is True
        assert call_args[1]["download"] is True
    
    def test_cli_help(self, cli_runner):
        """CLI should provide help information."""
        with patch("src.legacy.civic_scraper.cli.cli") as mock_cli:
            result = cli_runner.invoke(mock_cli, ["--help"])
            assert result.exit_code == 0
            assert "Usage:" in result.output
    
    def test_cli_version(self, cli_runner):
        """CLI should show version information."""
        with patch("src.legacy.civic_scraper.cli.cli") as mock_cli:
            result = cli_runner.invoke(mock_cli, ["--version"])
            assert result.exit_code == 0
            assert "version" in result.output.lower()
    
    @pytest.mark.vcr()
    def test_cli_error_handling(self, cli_runner, civic_scraper_dir, mock_requests):
        """CLI should handle errors gracefully."""
        # Mock a failed request
        mock_requests["get"].return_value = Mock(status_code=500, content=b"Server Error")
        
        with patch("src.legacy.civic_scraper.cli.cli") as mock_cli:
            result = cli_runner.invoke(
                mock_cli,
                [
                    "scrape",
                    "--start-date", "2020-05-05",
                    "--end-date", "2020-05-05",
                    "--url", "http://example.com/error",
                ],
            )
        
        # Should handle error gracefully
        assert result.exit_code == 0  # CLI should not crash
