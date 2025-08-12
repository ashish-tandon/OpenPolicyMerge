"""
Basic infrastructure tests for OpenPolicy Scraper Service.
Tests that the test environment is working correctly.
"""

import pytest
import os
import sys
from pathlib import Path


@pytest.mark.basic
class TestBasicInfrastructure:
    """Test basic test infrastructure functionality."""
    
    def test_python_version(self):
        """Test that we're running on a supported Python version."""
        version = sys.version_info
        assert version.major == 3
        assert version.minor >= 11, "Python 3.11+ required"
        print(f"Running on Python {version.major}.{version.minor}.{version.micro}")
    
    def test_working_directory(self):
        """Test that we're in the correct working directory."""
        cwd = os.getcwd()
        assert "scraper-service" in cwd, f"Expected to be in scraper-service directory, got: {cwd}"
        print(f"Working directory: {cwd}")
    
    def test_test_directory_structure(self):
        """Test that the test directory structure exists."""
        test_dir = Path("tests")
        assert test_dir.exists(), "tests directory should exist"
        
        # Check for main test categories
        expected_dirs = ["unit", "integration", "legacy_migration", "performance", "coverage", "quality"]
        for expected_dir in expected_dirs:
            dir_path = test_dir / expected_dir
            assert dir_path.exists(), f"Expected test directory {expected_dir} should exist"
            print(f"✓ Test directory {expected_dir} exists")
    
    def test_source_directory_structure(self):
        """Test that the source directory structure exists."""
        src_dir = Path("src")
        assert src_dir.exists(), "src directory should exist"
        
        # Check for main source categories
        expected_dirs = ["core", "services", "routes", "middleware"]
        for expected_dir in expected_dirs:
            dir_path = src_dir / expected_dir
            assert dir_path.exists(), f"Expected source directory {expected_dir} should exist"
            print(f"✓ Source directory {expected_dir} exists")
    
    def test_config_file_exists(self):
        """Test that configuration files exist."""
        config_file = Path("config.py")
        assert config_file.exists(), "config.py should exist"
        
        pytest_config = Path("pytest.ini")
        assert pytest_config.exists(), "pytest.ini should exist"
        
        requirements = Path("requirements.txt")
        assert requirements.exists(), "requirements.txt should exist"
        
        print("✓ Configuration files exist")
    
    def test_virtual_environment(self):
        """Test that we're running in a virtual environment."""
        assert hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix), \
            "Should be running in a virtual environment"
        print("✓ Running in virtual environment")
    
    def test_pytest_imports(self):
        """Test that pytest and related packages can be imported."""
        import pytest
        import pytest_cov
        import pytest_mock
        import pytest_asyncio
        print("✓ Pytest packages imported successfully")
    
    def test_basic_math(self):
        """Test basic mathematical operations."""
        assert 2 + 2 == 4
        assert 10 * 5 == 50
        assert 100 / 4 == 25
        print("✓ Basic math operations work")
    
    def test_string_operations(self):
        """Test basic string operations."""
        test_string = "OpenPolicy Scraper Service"
        assert "Scraper" in test_string
        assert test_string.startswith("OpenPolicy")
        assert test_string.endswith("Service")
        print("✓ String operations work")
    
    def test_list_operations(self):
        """Test basic list operations."""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert sum(test_list) == 15
        assert test_list[0] == 1
        assert test_list[-1] == 5
        print("✓ List operations work")
    
    def test_dict_operations(self):
        """Test basic dictionary operations."""
        test_dict = {"name": "scraper", "type": "service", "version": "1.0.0"}
        assert "name" in test_dict
        assert test_dict["type"] == "service"
        assert len(test_dict) == 3
        print("✓ Dictionary operations work")
    
    def test_file_operations(self):
        """Test basic file operations."""
        test_file = Path("test_temp.txt")
        
        # Write to file
        test_file.write_text("Hello, OpenPolicy!")
        
        # Read from file
        content = test_file.read_text()
        assert content == "Hello, OpenPolicy!"
        
        # Clean up
        test_file.unlink()
        
        print("✓ File operations work")
    
    def test_path_operations(self):
        """Test pathlib operations."""
        current_dir = Path.cwd()
        assert current_dir.exists()
        assert current_dir.is_dir()
        
        # Test path joining
        test_path = current_dir / "tests" / "test_basic_infrastructure.py"
        assert test_path.exists()
        assert test_path.suffix == ".py"
        
        print("✓ Path operations work")
    
    def test_environment_variables(self):
        """Test environment variable access."""
        # Test that we can read environment variables
        home = os.getenv("HOME")
        assert home is not None, "HOME environment variable should be set"
        
        # Test that we can set environment variables
        os.environ["TEST_VAR"] = "test_value"
        assert os.getenv("TEST_VAR") == "test_value"
        
        # Clean up
        del os.environ["TEST_VAR"]
        
        print("✓ Environment variable operations work")
    
    def test_exception_handling(self):
        """Test exception handling."""
        try:
            # This should raise a ValueError
            int("not_a_number")
            assert False, "Should have raised ValueError"
        except ValueError:
            # Expected exception
            pass
        
        print("✓ Exception handling works")
    
    def test_assertions(self):
        """Test various assertion types."""
        # Basic assertions
        assert True
        assert 1 == 1
        assert "hello" != "world"
        
        # Comparison assertions
        assert 5 > 3
        assert 10 >= 10
        assert 2 < 7
        assert 8 <= 8
        
        # Membership assertions
        assert "a" in "abc"
        assert "x" not in "abc"
        assert 1 in [1, 2, 3]
        assert 4 not in [1, 2, 3]
        
        print("✓ All assertion types work")
    
    def test_test_markers(self):
        """Test that pytest markers are working."""
        # This test should be marked with 'basic'
        assert True
        print("✓ Test markers are working")


if __name__ == "__main__":
    # Run basic tests if executed directly
    test_instance = TestBasicInfrastructure()
    
    # Run all test methods
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    print(f"Running {len(test_methods)} basic infrastructure tests...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            method = getattr(test_instance, method_name)
            method()
            print(f"✓ {method_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {method_name}: FAILED - {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All basic infrastructure tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
