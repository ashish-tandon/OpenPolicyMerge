# OpenPolicy Scraper Service Test Suite

This directory contains the comprehensive test suite for the OpenPolicy Scraper Service, including legacy scraper migration tests, unit tests, and integration tests.

## 🏗️ Test Structure

```
tests/
├── conftest.py                 # Shared test fixtures and configuration
├── legacy_migration/           # Legacy scraper migration tests
│   ├── civic_scraper/         # Civic-Scraper tests
│   │   ├── test_cli.py        # CLI functionality tests
│   │   ├── test_asset.py      # Asset management tests
│   │   └── platforms/         # Platform-specific tests
│   ├── openparliament/        # OpenParliament tests
│   │   ├── test_politicians.py # Politician data tests
│   │   └── test_jobs.py       # Daily run script tests
│   └── utils/                 # Utility function tests
├── integration/                # Integration tests
│   ├── test_scraper_service.py # Service integration tests
│   ├── test_data_pipeline.py  # Data pipeline tests
│   └── test_monitoring.py     # Monitoring integration tests
├── unit/                       # Unit tests
│   ├── test_models.py         # Data model tests
│   ├── test_scraper_manager.py # Scraper manager tests
│   └── test_routes.py         # API route tests
├── test_data/                  # Test data files
│   ├── civic_scraper/         # Civic-Scraper test data
│   └── openparliament/        # OpenParliament test data
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**: Python 3.11+ with virtual environment
2. **Dependencies**: Install test requirements
3. **Database**: PostgreSQL with PostGIS (for integration tests)

### Installation

```bash
# Navigate to scraper service directory
cd services/scraper-service

# Install test dependencies
pip install -r test-requirements.txt

# Or use the test runner script
./run_tests.sh
```

### Running Tests

#### Run All Tests
```bash
# Using pytest directly
pytest tests/ -v

# Using the test runner script
./run_tests.sh
```

#### Run Specific Test Categories
```bash
# Legacy migration tests
pytest tests/legacy_migration/ -v

# Integration tests
pytest tests/integration/ -v

# Unit tests
pytest tests/unit/ -v

# Civic-Scraper specific tests
pytest tests/legacy_migration/civic_scraper/ -v

# OpenParliament specific tests
pytest tests/legacy_migration/openparliament/ -v
```

#### Run Tests with Coverage
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Coverage report will be available at htmlcov/index.html
```

#### Run Tests in Parallel
```bash
# Run tests with multiple workers
pytest tests/ -n 4 --dist=worksteal
```

## 🧪 Test Categories

### 1. Legacy Migration Tests

#### Civic-Scraper Tests
- **CLI Tests**: Command-line interface functionality
- **Asset Tests**: Asset collection and management
- **Platform Tests**: PrimeGov, CivicPlus, Granicus, Legistar
- **Cache Tests**: Caching functionality
- **Validation Tests**: Data validation and error handling

#### OpenParliament Tests
- **Politician Tests**: MP data management and retrieval
- **Job Tests**: Daily run scripts and automation
- **Model Tests**: Django model functionality
- **Integration Tests**: Data pipeline and processing

### 2. Integration Tests
- **Service Integration**: Scraper service API endpoints
- **Data Pipeline**: End-to-end data processing
- **Monitoring**: Prometheus metrics and health checks
- **Database**: PostgreSQL integration and transactions

### 3. Unit Tests
- **Models**: Data models and validation
- **Services**: Business logic and service layer
- **Routes**: API endpoint handlers
- **Utilities**: Helper functions and utilities

## 📊 Test Coverage Requirements

- **Overall Service**: ≥85% statement coverage
- **Civic-Scraper**: ≥95% branch coverage
- **OpenParliament**: ≥85% statement coverage
- **New Code**: 100% coverage for new functionality

## 🔧 Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
```

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.legacy`: Legacy migration tests
- `@pytest.mark.civic_scraper`: Civic-Scraper specific tests
- `@pytest.mark.openparliament`: OpenParliament specific tests
- `@pytest.mark.slow`: Slow running tests
- `@pytest.mark.vcr`: Tests using VCR for HTTP mocking

## 🎯 Test Data Management

### Test Data Files
- **CSV Files**: Sample asset data for Civic-Scraper
- **JSON Files**: Sample politician data for OpenParliament
- **Fixtures**: Reusable test data and configurations

### Mock Data
- **HTTP Responses**: Mocked external API calls
- **Database**: In-memory SQLite for Django tests
- **Services**: Mocked external service dependencies

## 🚨 Error Handling Tests

### Expected Error Scenarios
- **Network Failures**: HTTP timeouts and connection errors
- **Data Validation**: Invalid input data and malformed responses
- **Authentication**: Unauthorized access and token expiration
- **Rate Limiting**: API rate limit exceeded
- **Database Errors**: Connection failures and constraint violations

### Error Recovery
- **Retry Logic**: Automatic retry mechanisms
- **Fallback Strategies**: Alternative data sources
- **Graceful Degradation**: Service continues with reduced functionality
- **Error Logging**: Comprehensive error tracking and reporting

## 📈 Performance Testing

### Benchmark Tests
- **Scraper Performance**: Execution time and resource usage
- **Data Processing**: Throughput and latency measurements
- **Concurrent Execution**: Multi-scraper performance
- **Memory Usage**: Memory consumption and garbage collection

### Load Testing
- **Concurrent Requests**: Multiple simultaneous API calls
- **Database Performance**: Query execution time and optimization
- **Network Latency**: External API response times

## 🔍 Code Quality Checks

### Pre-Test Checks
- **Black**: Code formatting validation
- **Ruff**: Linting and style checking
- **MyPy**: Type checking and validation
- **Import Sorting**: Import statement organization

### Quality Gates
- **Coverage Threshold**: Minimum coverage requirements
- **Linting Score**: Maximum allowed linting violations
- **Type Coverage**: Type annotation completeness
- **Documentation**: Docstring coverage and quality

## 🚀 Continuous Integration

### CI/CD Pipeline
- **Automated Testing**: Run tests on every commit
- **Coverage Reporting**: Track coverage trends over time
- **Quality Gates**: Block merges on test failures
- **Performance Monitoring**: Track test execution time

### Test Environments
- **Development**: Local development testing
- **Staging**: Pre-production validation
- **Production**: Production environment smoke tests

## 📚 Test Documentation

### Writing Tests
1. **Follow Naming Convention**: `test_<functionality>_<scenario>`
2. **Use Descriptive Names**: Clear test purpose and expected outcome
3. **Arrange-Act-Assert**: Structure tests in AAA pattern
4. **Mock External Dependencies**: Isolate unit under test
5. **Test Edge Cases**: Include boundary conditions and error scenarios

### Test Examples
```python
def test_scraper_creation_with_valid_config(self, sample_scraper_config):
    """Test scraper creation with valid configuration."""
    # Arrange
    manager = ScraperManager()
    
    # Act
    result = manager.create_scraper(sample_scraper_config)
    
    # Assert
    assert result["id"] == "test-scraper-1"
    assert result["name"] == "Test Scraper"
    assert result["status"] == "enabled"
```

## 🎯 Best Practices

### Test Design
- **Single Responsibility**: Each test focuses on one behavior
- **Independence**: Tests don't depend on each other
- **Repeatability**: Tests produce same results every time
- **Fast Execution**: Tests complete quickly for rapid feedback

### Data Management
- **Fresh Data**: Each test uses clean, isolated data
- **Minimal Setup**: Only create necessary test data
- **Cleanup**: Properly clean up after tests
- **Realistic Data**: Use realistic but minimal test data

### Mocking Strategy
- **External Services**: Mock HTTP calls and external APIs
- **Database**: Use test databases or in-memory alternatives
- **Time**: Mock time-dependent operations for consistent results
- **Randomness**: Seed random generators for reproducible tests

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Check Python path and virtual environment
2. **Database Connection**: Verify database configuration
3. **Mock Failures**: Ensure proper mock setup and teardown
4. **Coverage Issues**: Check source code paths and exclusions

### Debug Commands
```bash
# Run single test with verbose output
pytest tests/unit/test_scraper_manager.py::TestScraperManager::test_get_scrapers -v -s

# Run tests with debugger
pytest tests/ --pdb

# Generate coverage report for specific module
pytest tests/ --cov=src.services.scraper_manager --cov-report=term-missing
```

## 📞 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests in the project repository
- **Community**: Join the OpenPolicy community discussions

### Contributing
1. **Write Tests**: Add tests for new functionality
2. **Improve Coverage**: Identify and cover uncovered code paths
3. **Update Documentation**: Keep this README current
4. **Code Review**: Review test code for quality and completeness

---

**Note**: This test suite is designed to ensure the reliability and quality of the OpenPolicy Scraper Service. All tests should pass before deploying to production environments.
