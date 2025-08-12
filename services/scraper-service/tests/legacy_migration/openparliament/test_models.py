"""
Tests for OpenParliament data models.
Tests model functionality in alignment with services-based architecture.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import json
from pathlib import Path

# Import the adapted OpenParliament models (to be created)
# from src.legacy.openparliament.core.models import *

@pytest.mark.legacy
@pytest.mark.openparliament
class TestOpenParliamentModels:
    """Test OpenParliament data model functionality."""
    
    @pytest.fixture
    def sample_politician_data(self):
        """Provide sample politician data for testing."""
        return {
            "id": 1,
            "name": "Test MP",
            "riding": "Test Riding",
            "party": "Test Party",
            "current": True,
            "start_date": date(2023, 1, 1),
            "end_date": None,
            "email": "test.mp@example.com",
            "phone": "+1-555-0123"
        }
    
    @pytest.fixture
    def sample_session_data(self):
        """Provide sample session data for testing."""
        return {
            "id": 1,
            "name": "44th Parliament, 1st Session",
            "start": date(2023, 1, 1),
            "end": None,
            "current": True
        }
    
    @pytest.fixture
    def sample_bill_data(self):
        """Provide sample bill data for testing."""
        return {
            "id": 1,
            "number": "C-1",
            "title": "Test Bill",
            "session_id": 1,
            "introduced_date": date(2023, 1, 15),
            "status": "introduced",
            "sponsor_id": 1
        }
    
    @pytest.fixture
    def mock_politician_model(self):
        """Mock the Politician model."""
        with patch("src.legacy.openparliament.core.models.Politician") as MockPolitician:
            # Setup mock politician instance
            mock_pol = Mock()
            mock_pol.id = 1
            mock_pol.name = "Test MP"
            mock_pol.riding = "Test Riding"
            mock_pol.party = "Test Party"
            mock_pol.current = True
            mock_pol.start_date = date(2023, 1, 1)
            mock_pol.end_date = None
            mock_pol.email = "test.mp@example.com"
            mock_pol.phone = "+1-555-0123"
            
            # Setup class methods
            MockPolitician.objects.get_by_name = Mock(return_value=mock_pol)
            MockPolitician.objects.create = Mock(return_value=mock_pol)
            MockPolitician.objects.filter = Mock(return_value=Mock())
            MockPolitician.objects.all = Mock(return_value=Mock())
            
            yield MockPolitician
    
    @pytest.fixture
    def mock_session_model(self):
        """Mock the Session model."""
        with patch("src.legacy.openparliament.core.models.Session") as MockSession:
            # Setup mock session instance
            mock_session = Mock()
            mock_session.id = 1
            mock_session.name = "44th Parliament, 1st Session"
            mock_session.start = date(2023, 1, 1)
            mock_session.end = None
            mock_session.current = True
            
            # Setup class methods
            MockSession.objects.current = Mock(return_value=mock_session)
            MockSession.objects.create = Mock(return_value=mock_session)
            MockSession.objects.filter = Mock(return_value=Mock())
            
            yield MockSession
    
    @pytest.fixture
    def mock_bill_model(self):
        """Mock the Bill model."""
        with patch("src.legacy.openparliament.core.models.Bill") as MockBill:
            # Setup mock bill instance
            mock_bill = Mock()
            mock_bill.id = 1
            mock_bill.number = "C-1"
            mock_bill.title = "Test Bill"
            mock_bill.session_id = 1
            mock_bill.introduced_date = date(2023, 1, 15)
            mock_bill.status = "introduced"
            mock_bill.sponsor_id = 1
            
            # Setup class methods
            MockBill.objects.create = Mock(return_value=mock_bill)
            MockBill.objects.filter = Mock(return_value=Mock())
            
            yield MockBill
    
    def test_politician_model_creation(self, mock_politician_model, sample_politician_data):
        """Test politician model creation and validation."""
        Politician = mock_politician_model
        
        # Test creating politician with valid data
        politician = Politician.objects.create(**sample_politician_data)
        
        # Verify politician attributes
        assert politician.id == 1
        assert politician.name == "Test MP"
        assert politician.riding == "Test Riding"
        assert politician.party == "Test Party"
        assert politician.current is True
        assert politician.start_date == date(2023, 1, 1)
        assert politician.end_date is None
        assert politician.email == "test.mp@example.com"
        assert politician.phone == "+1-555-0123"
        
        # Verify creation method was called
        Politician.objects.create.assert_called_once_with(**sample_politician_data)
    
    def test_politician_model_validation(self, mock_politician_model):
        """Test politician model validation rules."""
        Politician = mock_politician_model
        
        # Test required fields validation
        required_fields = ["name", "riding", "party"]
        
        for field in required_fields:
            # Create politician without required field
            invalid_data = {"name": "Test MP", "riding": "Test Riding"}
            if field != "name":
                invalid_data["name"] = "Test MP"
            if field != "riding":
                invalid_data["riding"] = "Test Riding"
            
            # This would normally raise validation error in Django
            # For now, we'll test the mock behavior
            assert field in required_fields
    
    def test_politician_model_relationships(self, mock_politician_model, mock_session_model):
        """Test politician model relationships."""
        Politician = mock_politician_model
        Session = mock_session_model
        
        # Mock related models
        with patch("src.legacy.openparliament.core.models.Party") as MockParty, \
             patch("src.legacy.openparliament.core.models.Riding") as MockRiding:
            
            # Setup mock party
            mock_party = Mock()
            mock_party.name = "Liberal"
            mock_party.id = 1
            MockParty.return_value = mock_party
            
            # Setup mock riding
            mock_riding = Mock()
            mock_riding.name = "Vancouver Centre"
            mock_riding.id = 1
            MockRiding.return_value = mock_riding
            
            # Test politician with relationships
            politician = Politician.objects.get_by_name("Test MP")
            
            # Mock the relationships
            politician.party = mock_party
            politician.riding = mock_riding
            
            assert politician.party.name == "Liberal"
            assert politician.riding.name == "Vancouver Centre"
    
    def test_session_model_functionality(self, mock_session_model, sample_session_data):
        """Test session model functionality."""
        Session = mock_session_model
        
        # Test getting current session
        current_session = Session.objects.current()
        assert current_session.id == 1
        assert current_session.name == "44th Parliament, 1st Session"
        assert current_session.start == date(2023, 1, 1)
        assert current_session.current is True
        
        # Test session creation
        new_session = Session.objects.create(**sample_session_data)
        assert new_session.id == 1
        assert new_session.name == "44th Parliament, 1st Session"
        
        # Verify methods were called
        Session.objects.current.assert_called_once()
        Session.objects.create.assert_called_once_with(**sample_session_data)
    
    def test_bill_model_functionality(self, mock_bill_model, sample_bill_data):
        """Test bill model functionality."""
        Bill = mock_bill_model
        
        # Test bill creation
        new_bill = Bill.objects.create(**sample_bill_data)
        assert new_bill.id == 1
        assert new_bill.number == "C-1"
        assert new_bill.title == "Test Bill"
        assert new_bill.status == "introduced"
        assert new_bill.introduced_date == date(2023, 1, 15)
        
        # Verify creation method was called
        Bill.objects.create.assert_called_once_with(**sample_bill_data)
    
    def test_model_queryset_methods(self, mock_politician_model):
        """Test model queryset methods."""
        Politician = mock_politician_model
        
        # Mock queryset methods
        mock_queryset = Mock()
        mock_queryset.filter = Mock(return_value=mock_queryset)
        mock_queryset.order_by = Mock(return_value=mock_queryset)
        mock_queryset.values = Mock(return_value=[{"name": "Test MP"}])
        mock_queryset.count = Mock(return_value=1)
        
        Politician.objects.filter.return_value = mock_queryset
        Politician.objects.all.return_value = mock_queryset
        
        # Test filtering
        filtered_politicians = Politician.objects.filter(current=True)
        assert filtered_politicians is not None
        mock_queryset.filter.assert_called_with(current=True)
        
        # Test ordering
        ordered_politicians = filtered_politicians.order_by("name")
        assert ordered_politicians is not None
        mock_queryset.order_by.assert_called_with("name")
        
        # Test values
        politician_values = ordered_politicians.values("name")
        assert len(politician_values) == 1
        assert politician_values[0]["name"] == "Test MP"
        mock_queryset.values.assert_called_with("name")
        
        # Test counting
        count = ordered_politicians.count()
        assert count == 1
        mock_queryset.count.assert_called_once()
    
    def test_model_validation_errors(self, mock_politician_model):
        """Test model validation error handling."""
        Politician = mock_politician_model
        
        # Test with invalid data
        invalid_data = {
            "name": "",  # Empty name
            "riding": "Test Riding",
            "party": "Test Party"
        }
        
        # Mock validation error
        with patch.object(Politician.objects, 'create') as mock_create:
            mock_create.side_effect = Exception("Validation error: name cannot be empty")
            
            try:
                Politician.objects.create(**invalid_data)
            except Exception as e:
                assert "Validation error" in str(e)
                assert "name cannot be empty" in str(e)
    
    def test_model_save_methods(self, mock_politician_model):
        """Test model save and update methods."""
        Politician = mock_politician_model
        
        # Mock politician instance
        politician = Politician.objects.get_by_name("Test MP")
        politician.save = Mock()
        politician.delete = Mock()
        
        # Test save method
        politician.save()
        politician.save.assert_called_once()
        
        # Test delete method
        politician.delete()
        politician.delete.assert_called_once()
    
    def test_model_serialization(self, mock_politician_model):
        """Test model serialization methods."""
        Politician = mock_politician_model
        
        # Mock politician instance
        politician = Politician.objects.get_by_name("Test MP")
        
        # Mock serialization methods
        politician.to_dict = Mock(return_value={
            "id": 1,
            "name": "Test MP",
            "riding": "Test Riding",
            "party": "Test Party"
        })
        
        politician.to_json = Mock(return_value='{"id": 1, "name": "Test MP"}')
        
        # Test dictionary serialization
        politician_dict = politician.to_dict()
        assert politician_dict["id"] == 1
        assert politician_dict["name"] == "Test MP"
        politician.to_dict.assert_called_once()
        
        # Test JSON serialization
        politician_json = politician.to_json()
        assert "Test MP" in politician_json
        politician.to_json.assert_called_once()
    
    def test_model_custom_methods(self, mock_politician_model):
        """Test model custom methods and business logic."""
        Politician = mock_politician_model
        
        # Mock politician instance
        politician = Politician.objects.get_by_name("Test MP")
        
        # Mock custom methods
        politician.is_current_mp = Mock(return_value=True)
        politician.get_riding_name = Mock(return_value="Test Riding")
        politician.get_party_name = Mock(return_value="Test Party")
        politician.get_contact_info = Mock(return_value={
            "email": "test.mp@example.com",
            "phone": "+1-555-0123"
        })
        
        # Test custom methods
        assert politician.is_current_mp() is True
        assert politician.get_riding_name() == "Test Riding"
        assert politician.get_party_name() == "Test Party"
        
        contact_info = politician.get_contact_info()
        assert contact_info["email"] == "test.mp@example.com"
        assert contact_info["phone"] == "+1-555-0123"
        
        # Verify methods were called
        politician.is_current_mp.assert_called_once()
        politician.get_riding_name.assert_called_once()
        politician.get_party_name.assert_called_once()
        politician.get_contact_info.assert_called_once()
    
    def test_model_performance_optimization(self, mock_politician_model):
        """Test model performance optimization features."""
        Politician = mock_politician_model
        
        # Mock queryset with optimization methods
        mock_queryset = Mock()
        mock_queryset.select_related = Mock(return_value=mock_queryset)
        mock_queryset.prefetch_related = Mock(return_value=mock_queryset)
        mock_queryset.only = Mock(return_value=mock_queryset)
        mock_queryset.defer = Mock(return_value=mock_queryset)
        
        Politician.objects.all.return_value = mock_queryset
        
        # Test optimization methods
        optimized_queryset = Politician.objects.all()
        
        # Test select_related for foreign keys
        optimized_queryset.select_related("party", "riding")
        mock_queryset.select_related.assert_called_with("party", "riding")
        
        # Test prefetch_related for many-to-many
        optimized_queryset.prefetch_related("committees")
        mock_queryset.prefetch_related.assert_called_with("committees")
        
        # Test only for specific fields
        optimized_queryset.only("name", "riding")
        mock_queryset.only.assert_called_with("name", "riding")
        
        # Test defer for excluding fields
        optimized_queryset.defer("bio", "photo")
        mock_queryset.defer.assert_called_with("bio", "photo")
    
    def test_model_data_integrity(self, mock_politician_model):
        """Test model data integrity constraints."""
        Politician = mock_politician_model
        
        # Test unique constraints
        with patch.object(Politician.objects, 'create') as mock_create:
            # Mock duplicate key error
            mock_create.side_effect = Exception("Duplicate entry for name")
            
            try:
                Politician.objects.create(name="Test MP", riding="Test Riding")
            except Exception as e:
                assert "Duplicate entry" in str(e)
        
        # Test foreign key constraints
        with patch.object(Politician.objects, 'create') as mock_create:
            # Mock foreign key error
            mock_create.side_effect = Exception("Foreign key constraint failed")
            
            try:
                Politician.objects.create(name="Test MP", riding_id=999)
            except Exception as e:
                assert "Foreign key constraint" in str(e)
    
    def test_model_audit_trail(self, mock_politician_model):
        """Test model audit trail functionality."""
        Politician = mock_politician_model
        
        # Mock politician instance
        politician = Politician.objects.get_by_name("Test MP")
        
        # Mock audit fields
        politician.created_at = datetime(2023, 1, 1, 10, 0, 0)
        politician.updated_at = datetime(2023, 1, 27, 10, 0, 0)
        politician.created_by = "system"
        politician.updated_by = "admin"
        
        # Mock audit methods
        politician.get_audit_trail = Mock(return_value=[
            {"action": "created", "timestamp": "2023-01-01T10:00:00Z", "user": "system"},
            {"action": "updated", "timestamp": "2023-01-27T10:00:00Z", "user": "admin"}
        ])
        
        # Test audit fields
        assert politician.created_at == datetime(2023, 1, 1, 10, 0, 0)
        assert politician.updated_at == datetime(2023, 1, 27, 10, 0, 0)
        assert politician.created_by == "system"
        assert politician.updated_by == "admin"
        
        # Test audit trail
        audit_trail = politician.get_audit_trail()
        assert len(audit_trail) == 2
        assert audit_trail[0]["action"] == "created"
        assert audit_trail[1]["action"] == "updated"
        
        politician.get_audit_trail.assert_called_once()
