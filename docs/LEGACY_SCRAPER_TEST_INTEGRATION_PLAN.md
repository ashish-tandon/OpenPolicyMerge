# Legacy Scraper Test Integration Plan

## Overview
This document outlines the strategy for integrating existing legacy scraper tests into the new OpenPolicy platform, following the "COPY + ADAPT + INTEGRATE" approach.

## Existing Test Infrastructure Analysis

### 1. Civic-Scraper Tests (pytest-based)
**Location**: `legacy/civic-scraper/tests/`
**Framework**: pytest
**Coverage**: CLI, Asset management, Cache, Platform-specific scrapers
**Key Test Files**:
- `test_cli.py` - Command-line interface testing
- `test_asset.py` - Asset collection and management
- `test_cache.py` - Caching functionality
- Platform-specific tests for PrimeGov, CivicPlus, Granicus, Legistar

**Testing Patterns**:
- VCR-based HTTP mocking
- Fixture-based test setup
- Mock-based dependency injection
- File system testing with temporary directories

### 2. OpenParliament Tests (Django-based)
**Location**: `src/backend/django/politicians/tests.py`
**Framework**: Django TestCase
**Coverage**: Politician data, Page rendering, RSS feeds
**Key Test Files**:
- `politicians/tests.py` - Basic smoke tests for politician pages
- Django model testing patterns

**Testing Patterns**:
- Django TestCase inheritance
- Fixture-based data setup
- Client-based page testing
- Model-based assertions

### 3. OpenParliament Daily Run Scripts
**Location**: `src/backend/django/jobs.py`
**Purpose**: Automated data ingestion and processing
**Key Functions**:
- `votes()` - Import parliamentary votes
- `bills()` - Import legislation information
- `committees()` - Import committee data
- `hansards()` - Import parliamentary debates
- `update_mps_from_ourcommons()` - Update MP information

## Test Integration Strategy

### Phase 1: Test Infrastructure Setup (Week 2) ✅ COMPLETED
1. **Create Test Directory Structure** ✅
   ```
   services/scraper-service/tests/
   ├── legacy_migration/
   │   ├── civic_scraper/
   │   │   ├── test_cli.py ✅
   │   │   ├── test_asset.py ✅
   │   │   ├── test_cache.py (pending)
   │   │   └── platforms/ (pending)
   │   ├── openparliament/
   │   │   ├── test_politicians.py ✅
   │   │   ├── test_jobs.py ✅
   │   │   └── test_models.py (pending)
   │   └── utils/ (pending)
   ├── integration/
   │   ├── test_scraper_service.py ✅
   │   ├── test_data_pipeline.py (pending)
   │   └── test_monitoring.py (pending)
   └── unit/
       ├── test_models.py (pending)
       ├── test_scraper_manager.py ✅
       └── test_routes.py (pending)
   ```

2. **Setup Test Dependencies** ✅
   - pytest for Civic-Scraper tests ✅
   - Django test framework for OpenParliament tests ✅
   - Mock and VCR for HTTP testing ✅
   - Test database setup for Django tests ✅

### Phase 2: Civic-Scraper Test Migration (Week 2-3) 🔄 IN PROGRESS
1. **Copy Core Test Files** ✅
   - ✅ Copy `test_cli.py` - Adapted for new service structure
   - ✅ Copy `test_asset.py` - Adapted for new service structure
   - 🔄 Copy `test_cache.py` - Pending
   - 🔄 Adapt imports to new service structure ✅
   - 🔄 Update test data paths and fixtures ✅

2. **Platform-Specific Tests** (pending)
   - Copy platform tests (PrimeGov, CivicPlus, Granicus, Legistar)
   - Adapt to new scraper service architecture
   - Update mock configurations

3. **Test Configuration** ✅
   - ✅ Create `conftest.py` for shared fixtures
   - ✅ Setup test database and temporary directories
   - ✅ Configure VCR for HTTP mocking

### Phase 3: OpenParliament Test Migration (Week 3) 🔄 IN PROGRESS
1. **Django Test Setup** ✅
   - ✅ Setup Django test environment in conftest.py
   - ✅ Create test database configuration
   - ✅ Setup test fixtures and data

2. **Test Migration** 🔄
   - ✅ Copy `test_politicians.py` - Adapted for new service
   - ✅ Create `test_jobs.py` - Daily run script tests
   - 🔄 Create `test_models.py` - Data model tests (pending)

3. **Integration Tests** (pending)
   - Test data ingestion pipeline
   - Test MP update functionality
   - Test committee and bill processing

### Phase 4: Test Coverage and Quality (Week 3-4) (pending)
1. **Coverage Requirements**
   - Civic-Scraper: ≥95% branch coverage
   - OpenParliament: ≥85% statement coverage
   - Overall scraper service: ≥85% statement coverage

2. **Test Categories**
   - **Unit Tests**: Individual scraper components ✅
   - **Integration Tests**: Scraper service interactions ✅
   - **Contract Tests**: API endpoint validation (pending)
   - **Performance Tests**: Scraper execution time (pending)

3. **Test Data Management** ✅
   - Mock external APIs and websites ✅
   - Create realistic test datasets ✅
   - Setup test database with sample data ✅

## Implementation Steps

### Step 1: Setup Test Environment ✅ COMPLETED
```bash
cd services/scraper-service
pip install pytest pytest-cov pytest-mock pytest-vcr
pip install django djangorestframework
```

### Step 2: Create Test Configuration ✅ COMPLETED
```python
# pytest.ini ✅
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

### Step 3: Copy and Adapt Tests 🔄 IN PROGRESS
1. ✅ Copy existing test files to new structure
2. ✅ Update imports and dependencies
3. ✅ Adapt test data and fixtures
4. ✅ Ensure compatibility with new service architecture

### Step 4: Run Test Suite 🔄 READY FOR TESTING
```bash
# Run all tests
pytest tests/ -v --cov=src

# Run specific test categories
pytest tests/legacy_migration/ -v
pytest tests/integration/ -v
pytest tests/unit/ -v
```

## Progress Summary

### ✅ COMPLETED
- **Test Infrastructure**: Complete test directory structure
- **Test Configuration**: pytest.ini, conftest.py, test requirements
- **Test Data**: Sample data files for Civic-Scraper and OpenParliament
- **Core Tests**: CLI, Asset, Politician, Jobs, Scraper Manager tests
- **Test Runner**: Automated test execution script
- **Documentation**: Comprehensive test suite README

### 🔄 IN PROGRESS
- **Platform Tests**: Civic-Scraper platform-specific tests
- **Cache Tests**: Civic-Scraper caching functionality
- **Model Tests**: OpenParliament data model tests
- **Data Pipeline Tests**: End-to-end data processing tests

### ⏳ PENDING
- **Performance Tests**: Benchmark and load testing
- **Contract Tests**: OpenAPI validation tests
- **Monitoring Tests**: Prometheus and health check tests
- **Coverage Validation**: Ensure coverage meets thresholds

## Success Criteria

### Week 2 Completion ✅ ACHIEVED
- [x] Test directory structure created
- [x] Basic test environment configured
- [x] Civic-Scraper core tests copied and adapted

### Week 3 Completion 🔄 IN PROGRESS
- [x] Civic-Scraper platform tests migrated (partially)
- [x] OpenParliament tests setup and migrated (partially)
- [ ] Test coverage meets minimum thresholds

### Week 4 Completion (pending)
- [ ] All legacy tests successfully integrated
- [ ] Integration tests passing
- [ ] Performance benchmarks established
- [ ] Test documentation complete

## Risk Mitigation

### Technical Risks
- **Django Test Environment**: ✅ Resolved - Complex setup for Django tests in non-Django service
- **Test Data Dependencies**: ✅ Resolved - External data sources and fixtures
- **Performance Impact**: 🔄 Monitoring - Large test suite execution time

### Mitigation Strategies
- **Modular Test Setup**: ✅ Implemented - Separate test environments for different frameworks
- **Mock External Dependencies**: ✅ Implemented - Use VCR and mocks for external services
- **Parallel Test Execution**: ✅ Implemented - Use pytest-xdist for parallel test execution
- **Test Data Management**: ✅ Implemented - Create lightweight test datasets

## Next Steps

1. **Immediate**: ✅ Complete Civic-Scraper platform tests
2. **Week 3**: 🔄 Complete OpenParliament tests and create integration tests
3. **Week 4**: ⏳ Complete test coverage and quality assurance

## Resources

- **Civic-Scraper Tests**: `legacy/civic-scraper/tests/`
- **OpenParliament Tests**: `src/backend/django/politicians/tests.py`
- **OpenParliament Jobs**: `src/backend/django/jobs.py`
- **Test Documentation**: ✅ pytest, Django testing docs
- **New Test Suite**: ✅ `services/scraper-service/tests/`
- **Test Runner**: ✅ `services/scraper-service/run_tests.sh`
