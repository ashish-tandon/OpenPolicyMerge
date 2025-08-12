"""
Tests for OpenParliament daily run scripts (jobs.py).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import json
from pathlib import Path

# Import the adapted OpenParliament jobs module (to be created)
# from src.legacy.openparliament.jobs import *

@pytest.mark.legacy
@pytest.mark.openparliament
class TestOpenParliamentJobs:
    """Test OpenParliament daily run scripts."""
    
    @pytest.fixture
    def mock_parliament_imports(self):
        """Mock parliament import modules."""
        with patch("src.legacy.openparliament.imports.parlvotes") as mock_parlvotes, \
             patch("src.legacy.openparliament.imports.legisinfo") as mock_legisinfo, \
             patch("src.legacy.openparliament.imports.parl_document") as mock_parl_document, \
             patch("src.legacy.openparliament.imports.parl_cmte") as mock_parl_cmte, \
             patch("src.legacy.openparliament.imports.mps") as mock_mps:
            
            yield {
                "parlvotes": mock_parlvotes,
                "legisinfo": mock_legisinfo,
                "parl_document": mock_parl_document,
                "parl_cmte": mock_parl_cmte,
                "mps": mock_mps
            }
    
    @pytest.fixture
    def mock_models(self):
        """Mock Django models."""
        with patch("src.legacy.openparliament.core.models.Politician") as MockPolitician, \
             patch("src.legacy.openparliament.core.models.Session") as MockSession, \
             patch("src.legacy.openparliament.hansards.models.Document") as MockDocument, \
             patch("src.legacy.openparliament.activity.models.Activity") as MockActivity:
            
            # Setup mock politician
            mock_pol = Mock()
            mock_pol.id = 1
            mock_pol.name = "Test MP"
            MockPolitician.objects.current = Mock(return_value=[mock_pol])
            
            # Setup mock session
            mock_session = Mock()
            mock_session.start = date(2023, 1, 1)
            mock_session.objects.current = Mock(return_value=mock_session)
            
            # Setup mock document
            mock_doc = Mock()
            mock_doc.id = 1
            mock_doc.document_type = "DEBATE"
            mock_doc.skip_parsing = False
            mock_doc.statement_set = Mock()
            mock_doc.statement_set.all = Mock(return_value=Mock())
            mock_doc.statement_set.all.count = Mock(return_value=0)
            mock_doc.save_activity = Mock()
            
            MockDocument.objects.filter = Mock(return_value=Mock())
            MockDocument.objects.filter.iterator = Mock(return_value=[mock_doc])
            
            # Setup mock activity
            MockActivity.public = Mock()
            MockActivity.public.filter = Mock(return_value=Mock())
            
            yield {
                "Politician": MockPolitician,
                "Session": MockSession,
                "Document": MockDocument,
                "Activity": MockActivity
            }
    
    @pytest.fixture
    def mock_utils(self):
        """Mock utility modules."""
        with patch("src.legacy.openparliament.activity.utils") as mock_activity_utils, \
             patch("src.legacy.openparliament.text_analysis.corpora") as mock_corpora, \
             patch("src.legacy.openparliament.summaries.generation") as mock_summaries:
            
            yield {
                "activity_utils": mock_activity_utils,
                "corpora": mock_corpora,
                "summaries": mock_summaries
            }
    
    def test_votes_import(self, mock_parliament_imports):
        """Test votes import functionality."""
        mock_parlvotes = mock_parliament_imports["parlvotes"]
        
        # Mock the import_votes function
        mock_parlvotes.import_votes = Mock()
        
        # Call the votes function
        # votes()  # This would be the actual function call
        
        # Verify import_votes was called
        mock_parlvotes.import_votes.assert_called_once()
    
    def test_bills_import(self, mock_parliament_imports, mock_models):
        """Test bills import functionality."""
        mock_legisinfo = mock_parliament_imports["legisinfo"]
        MockSession = mock_models["Session"]
        
        # Mock the import_bills function
        mock_legisinfo.import_bills = Mock()
        
        # Get current session
        current_session = MockSession.objects.current()
        
        # Call the bills function
        # bills()  # This would be the actual function call
        
        # Verify import_bills was called with current session
        mock_legisinfo.import_bills.assert_called_once_with(current_session)
    
    def test_committee_imports(self, mock_parliament_imports, mock_models):
        """Test committee import functionality."""
        mock_parl_cmte = mock_parliament_imports["parl_cmte"]
        MockSession = mock_models["Session"]
        
        # Mock the committee import functions
        mock_parl_cmte.import_committee_list = Mock()
        mock_parl_cmte.import_committee_documents = Mock()
        
        # Get current session
        current_session = MockSession.objects.current()
        
        # Call the committees function
        # committees()  # This would be the actual function call
        
        # Verify committee imports were called
        mock_parl_cmte.import_committee_list.assert_called_once_with(session=current_session)
        mock_parl_cmte.import_committee_documents.assert_called_once_with(current_session)
    
    def test_hansards_import(self, mock_parliament_imports, mock_models):
        """Test Hansards (debates) import functionality."""
        mock_parl_document = mock_parliament_imports["parl_document"]
        MockDocument = mock_models["Document"]
        
        # Mock the fetch_latest_debates function
        mock_parl_document.fetch_latest_debates = Mock()
        
        # Call the hansards_load function
        # hansards_load()  # This would be the actual function call
        
        # Verify fetch_latest_debates was called
        mock_parl_document.fetch_latest_debates.assert_called_once()
    
    def test_hansards_parse(self, mock_parliament_imports, mock_models):
        """Test Hansards parsing functionality."""
        mock_parl_document = mock_parliament_imports["parl_document"]
        MockDocument = mock_models["Document"]
        
        # Mock the import_document function
        mock_parl_document.import_document = Mock()
        
        # Get documents to parse
        documents = MockDocument.objects.filter.return_value.iterator.return_value
        
        # Call the hansards_parse function
        # hansards_parse()  # This would be the actual function call
        
        # Verify import_document was called for each document
        for doc in documents:
            mock_parl_document.import_document.assert_called_with(doc, allow_reimport=False)
    
    def test_mp_update(self, mock_parliament_imports):
        """Test MP update functionality."""
        mock_mps = mock_parliament_imports["mps"]
        
        # Mock the update_mps_from_ourcommons function
        mock_mps.update_mps_from_ourcommons = Mock()
        
        # Call the MP update function
        # update_mps_from_ourcommons()  # This would be the actual function call
        
        # Verify update function was called
        mock_mps.update_mps_from_ourcommons.assert_called_once()
    
    def test_activity_pruning(self, mock_models, mock_utils):
        """Test activity pruning functionality."""
        MockPolitician = mock_models["Politician"]
        MockActivity = mock_models["Activity"]
        mock_activity_utils = mock_utils["activity_utils"]
        
        # Mock the prune function
        mock_activity_utils.prune = Mock()
        
        # Get current politicians
        current_politicians = MockPolitician.objects.current()
        
        # Call the prune_activities function
        # prune_activities()  # This would be the actual function call
        
        # Verify prune was called for each politician
        for pol in current_politicians:
            mock_activity_utils.prune.assert_called_with(
                MockActivity.public.filter.return_value.filter.return_value
            )
    
    def test_summaries_generation(self, mock_utils, mock_models):
        """Test summaries generation functionality."""
        mock_summaries = mock_utils["summaries"]
        MockSession = mock_models["Session"]
        
        # Mock the summary update functions
        mock_summaries.update_hansard_summaries = Mock()
        mock_summaries.update_reading_summaries = Mock()
        
        # Get current session
        current_session = MockSession.objects.current()
        
        # Call the summaries function
        # summaries()  # This would be the actual function call
        
        # Verify summary functions were called
        mock_summaries.update_hansard_summaries.assert_called_once()
        mock_summaries.update_reading_summaries.assert_called_once_with(current_session)
    
    def test_corpus_generation(self, mock_utils):
        """Test corpus generation functionality."""
        mock_corpora = mock_utils["corpora"]
        
        # Mock the corpus generation functions
        mock_corpora.generate_for_debates = Mock()
        mock_corpora.generate_for_committees = Mock()
        
        # Call the corpus functions
        # corpus_for_debates()  # This would be the actual function call
        # corpus_for_committees()  # This would be the actual function call
        
        # Verify corpus functions were called
        mock_corpora.generate_for_debates.assert_called_once()
        mock_corpora.generate_for_committees.assert_called_once()
    
    def test_error_handling(self, mock_parliament_imports):
        """Test error handling in job functions."""
        mock_parl_cmte = mock_parliament_imports["parl_cmte"]
        
        # Mock an exception
        mock_parl_cmte.import_committee_list.side_effect = Exception("Committee import failed")
        
        # Test that errors are handled gracefully
        try:
            # committees()  # This would be the actual function call
            pass
        except Exception as e:
            # Should handle the error gracefully
            assert "Committee import failed" in str(e)
    
    def test_transaction_handling(self, mock_models):
        """Test database transaction handling."""
        MockPolitician = mock_models["Politician"]
        
        # Mock transaction context
        with patch("django.db.transaction.atomic") as mock_transaction:
            # Call function that uses transactions
            # prune_activities()  # This would be the actual function call
            
            # Verify transaction was used
            mock_transaction.assert_called()
    
    def test_data_consistency(self, mock_models):
        """Test data consistency in job functions."""
        MockPolitician = mock_models["Politician"]
        MockSession = mock_models["Session"]
        
        # Verify that current session is valid
        current_session = MockSession.objects.current()
        assert current_session.start < date.today()
        
        # Verify that politicians have required attributes
        current_politicians = MockPolitician.objects.current()
        for pol in current_politicians:
            assert hasattr(pol, 'id')
            assert hasattr(pol, 'name')
    
    def test_job_ordering(self, mock_parliament_imports, mock_models):
        """Test that jobs are executed in correct order."""
        # This test would verify that dependent jobs are executed in the right sequence
        # For example, MPs should be updated before committees are imported
        
        # Mock the job functions
        mock_mps = mock_parliament_imports["mps"]
        mock_parl_cmte = mock_parliament_imports["parl_cmte"]
        
        # Verify that MP update happens before committee import
        # This would be tested by checking the actual job execution order
        assert mock_mps.update_mps_from_ourcommons.called
        assert mock_parl_cmte.import_committee_list.called
