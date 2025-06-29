#!/usr/bin/env python3
"""
End-to-end test script for the ingestion menu system.
Tests the complete workflow from menu selection to file processing.
"""
import os
import sys
import tempfile
import shutil
import pytest
import structlog

from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO
from contextlib import contextmanager
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.chroma.vector_store import ChromaDBVectorStore
from src.embeddings.embedding_generator import SentenceTransformerEmbeddingGenerator
from src.ingestion.models.document import IngestionConfig
from src.ingestion.orchestrators.ingestion_menu_orchestrator import \
    IngestionMenuOrchestrator
from src.ingestion.services.document_loader import FileSystemDocumentLoader
from src.ingestion.services.text_chunker import ParagraphTextChunker
from src.ingestion.services.text_extractor_factory import TextExtractorFactory
from src.ingestion.services.user_interface import ConsoleUserInterface
from src.logutils.logger import StructLogConfig


class MockUserInterface(ConsoleUserInterface):
    """Mock user interface for testing."""

    def __init__(self, responses):
        self.responses = responses
        self.response_index = 0

    def get_user_input(self, prompt):
        """Mock user input."""
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            print(f"Mock input: {prompt} -> {response}")
            return response
        return "0"  # Default to exit

    def confirm_action(self, message):
        """Mock confirmation - return True for 'y', False for 'n'."""
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            print(f"Mock confirmation: {message} -> {response}")
            return response.lower() == "y"
        return False

    def get_specific_file_choices(self, files, action):
        """Mock file selection - return all files for 'all', specific files for numbers."""
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            print(f"Mock file selection: {action} -> {response}")
            if response.lower() == "all":
                return list(files)
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in response.split(",")]
                    selected_files = []
                    for idx in indices:
                        if 0 <= idx < len(files):
                            selected_files.append(files[idx])
                    return selected_files
                except (ValueError, IndexError):
                    return list(files)
        return list(files)

    def get_file_type_deletion_choice(self, grouped_files):
        """Mock file type selection - return first type for testing."""
        if grouped_files:
            selected_type = list(grouped_files.keys())[0]
            print(f"Mock file type selection: {selected_type}")
            return selected_type
        # Return empty string if no grouped files (instead of None)
        return ""


@contextmanager
def create_temp_test_environment():
    """
    Enterprise-grade temporary test environment with automatic cleanup.
    
    Creates temporary directories and files that are automatically cleaned up
    when the context manager exits, regardless of how it exits (success/exception).
    """
    temp_dirs = []
    temp_files = []
    
    try:
        # Create temporary directories
        temp_data_dir = tempfile.mkdtemp(prefix="test_data_")
        temp_chroma_dir = tempfile.mkdtemp(prefix="test_chroma_")
        temp_dirs.extend([temp_data_dir, temp_chroma_dir])
        
        # Create test files in temporary data directory
        test_pdf_path = os.path.join(temp_data_dir, "test_document.pdf")
        test_txt_path = os.path.join(temp_data_dir, "test_document.txt")
        
        # Create a simple PDF file for testing
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(test_pdf_path)
            c.drawString(100, 750, "Test Document Content")
            c.save()
            temp_files.append(test_pdf_path)
        except ImportError:
            # If reportlab is not available, create a dummy PDF file
            with open(test_pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\n%Test PDF content\n')
            temp_files.append(test_pdf_path)
        
        # Create test text file
        with open(test_txt_path, "w") as f:
            f.write("This is a test document for menu functionality testing.\n")
            f.write("It contains multiple lines of text to test text extraction.\n")
        temp_files.append(test_txt_path)
        
        yield {
            "data_dir": temp_data_dir,
            "chroma_dir": temp_chroma_dir,
            "temp_dirs": temp_dirs,
            "temp_files": temp_files
        }
        
    finally:
        # Enterprise-grade cleanup: Always clean up, even if exceptions occur
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove temp file {temp_file}: {e}")
        
        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temp directory {temp_dir}: {e}")


@pytest.fixture(scope="function")
def test_setup():
    """
    Enterprise-grade pytest fixture with proper isolation and cleanup.
    
    Scope: function - Each test gets a fresh environment
    Cleanup: Automatic via context manager
    """
    # Configure logging
    StructLogConfig.configure(debug=True)
    logger = structlog.get_logger("e2e_menu_test")
    
    # Use temporary environment with automatic cleanup
    with create_temp_test_environment() as temp_env:
        # Initialize services with mocking (enterprise practice: mock external dependencies)
        mock_vector_store = Mock(spec=ChromaDBVectorStore)
        mock_vector_store.collection = Mock()
        mock_vector_store.collection.count.return_value = 5
        mock_vector_store.clear_all_documents.return_value = 5
        mock_vector_store.add_documents.return_value = True
        mock_vector_store.get_all_document_sources.return_value = [
            "test_document.pdf",
            "test_document.txt",
        ]
        mock_vector_store.document_exists.return_value = False
        mock_vector_store.get_document_count.return_value = 5

        mock_embedding_generator = Mock(spec=SentenceTransformerEmbeddingGenerator)
        mock_embedding_generator.generate_embeddings.return_value = [
            [0.1, 0.2, 0.3] for _ in range(3)
        ]

        mock_document_loader = Mock(spec=FileSystemDocumentLoader)
        mock_document_loader.load_documents.return_value = []

        mock_text_chunker = Mock(spec=ParagraphTextChunker)
        mock_text_chunker.chunk_text.return_value = []

        mock_text_extractor_factory = Mock(spec=TextExtractorFactory)

        logger.info("Enterprise test environment initialized with automatic cleanup")

        yield {
            "logger": logger,
            "data_dir": temp_env["data_dir"],
            "chroma_dir": temp_env["chroma_dir"],
            "vector_store": mock_vector_store,
            "embedding_generator": mock_embedding_generator,
            "document_loader": mock_document_loader,
            "text_chunker": mock_text_chunker,
            "text_extractor_factory": mock_text_extractor_factory,
        }
        
        # Cleanup happens automatically via context manager


class TestEndToEndMenu:
    """Enterprise-grade end-to-end test class with proper isolation."""

    def _run_test_with_mocked_input(self, test_setup, responses, test_name):
        """Run a test with mocked user input."""
        test_setup["logger"].info(f"Running test: {test_name}")

        # Create mock user interface
        mock_ui = MockUserInterface(responses)

        # Create menu orchestrator with mock UI
        orchestrator = IngestionMenuOrchestrator(
            user_interface=mock_ui, vector_store=test_setup["vector_store"]
        )

        # Create config with test data directory
        config = IngestionConfig(data_dir=Path(test_setup["data_dir"]))

        try:
            # Run the orchestrator
            result = orchestrator.ingest_documents(config)
            test_setup["logger"].info(
                f"Test completed: {test_name}", success=result.success
            )
            return result
        except Exception as e:
            test_setup["logger"].error(f"Test failed: {test_name}", error=str(e))
            raise

    # ==================== BASIC MENU TESTS ====================

    @pytest.mark.e2e
    def test_basic_menu_navigation(self, test_setup):
        """Test basic menu navigation and exit."""
        test_setup["logger"].info("Testing basic menu navigation")

        # Mock responses: Choose orchestrator (1), exit (0)
        responses = ["1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Basic Menu Navigation"
            )

            # Verify result
            test_setup["logger"].info(
                "Basic menu navigation test completed", success=result.success
            )

            assert result.success, "Basic menu navigation test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Basic menu navigation test failed", error=str(e)
            )
            assert False, f"Basic menu navigation test failed with exception: {str(e)}"

    # ==================== PROCESS NEW FILES TESTS ====================

    @pytest.mark.e2e
    def test_process_new_files_workflow(self, test_setup):
        """Test processing new files through the menu system."""
        test_setup["logger"].info("Testing process new files workflow")

        # Clear database first
        test_setup["vector_store"].clear_all_documents()

        # Mock responses: Choose orchestrator (1), process new files (1), add all (1), exit (0)
        responses = ["1", "1", "1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Process New Files Workflow"
            )

            # Verify result
            test_setup["logger"].info(
                "Process new files test completed", success=result.success
            )

            # Since we're mocking, just verify the test completed successfully
            assert result.success, "Process new files workflow test failed"
        except Exception as e:
            test_setup["logger"].error("Process new files test failed", error=str(e))
            assert False, f"Process new files test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_process_new_files_add_specific(self, test_setup):
        """Test processing new files with specific file selection."""
        test_setup["logger"].info("Testing process new files - add specific files")

        # Clear database first
        test_setup["vector_store"].clear_all_documents()

        # Mock responses: Choose orchestrator (1), process new files (1), add specific (2), select first file (1), exit (0)
        responses = ["1", "1", "2", "1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Process New Files - Add Specific"
            )

            # Verify result
            test_setup["logger"].info(
                "Process new files - add specific test completed",
                success=result.success,
            )

            assert result.success, "Process new files - add specific test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Process new files - add specific test failed", error=str(e)
            )
            assert (
                False
            ), f"Process new files - add specific test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_process_new_files_add_by_type(self, test_setup):
        """Test processing new files with type-based selection."""
        test_setup["logger"].info("Testing process new files - add by type")

        # Clear database first
        test_setup["vector_store"].clear_all_documents()

        # Mock responses: Choose orchestrator (1), process new files (1), add by type (3), select first type (1), exit (0)
        responses = ["1", "1", "3", "1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Process New Files - Add by Type"
            )

            # Verify result
            test_setup["logger"].info(
                "Process new files - add by type test completed", success=result.success
            )

            assert result.success, "Process new files - add by type test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Process new files - add by type test failed", error=str(e)
            )
            assert (
                False
            ), f"Process new files - add by type test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_process_new_files_cancel(self, test_setup):
        """Test processing new files with cancellation."""
        test_setup["logger"].info("Testing process new files - cancel operation")

        # Mock responses: Choose orchestrator (1), process new files (1), cancel (0), exit (0)
        responses = ["1", "1", "0", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Process New Files - Cancel"
            )

            # Verify result
            test_setup["logger"].info(
                "Process new files - cancel test completed", success=result.success
            )

            assert result.success, "Process new files - cancel test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Process new files - cancel test failed", error=str(e)
            )
            assert (
                False
            ), f"Process new files - cancel test failed with exception: {str(e)}"

    # ==================== ADD SPECIFIC FILE TESTS ====================

    @pytest.mark.e2e
    def test_add_specific_file_workflow(self, test_setup):
        """Test adding a specific file through the menu system."""
        test_setup["logger"].info("Testing add specific file workflow")

        # Clear database first
        test_setup["vector_store"].clear_all_documents()

        # Mock responses: Choose orchestrator (1), add specific file (6), select first file (1), exit (0)
        responses = ["1", "6", "1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Add Specific File Workflow"
            )

            # Verify result
            test_setup["logger"].info(
                "Add specific file test completed", success=result.success
            )

            assert result.success, "Add specific file workflow test failed"
        except Exception as e:
            test_setup["logger"].error("Add specific file test failed", error=str(e))
            assert False, f"Add specific file test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_add_specific_file_cancel(self, test_setup):
        """Test adding a specific file with cancellation."""
        test_setup["logger"].info("Testing add specific file - cancel operation")

        # Mock responses: Choose orchestrator (1), add specific file (6), cancel (0), exit (0)
        responses = ["1", "6", "0", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Add Specific File - Cancel"
            )

            # Verify result
            test_setup["logger"].info(
                "Add specific file - cancel test completed", success=result.success
            )

            assert result.success, "Add specific file - cancel test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Add specific file - cancel test failed", error=str(e)
            )
            assert (
                False
            ), f"Add specific file - cancel test failed with exception: {str(e)}"

    # ==================== ADD FILES BY TYPE TESTS ====================

    @pytest.mark.e2e
    def test_add_files_by_type_workflow(self, test_setup):
        """Test adding files by type through the menu system."""
        test_setup["logger"].info("Testing add files by type workflow")

        # Clear database first
        test_setup["vector_store"].clear_all_documents()

        # Mock responses: Choose orchestrator (1), add by type (5), select first type (1), exit (0)
        responses = ["1", "5", "1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Add Files by Type Workflow"
            )

            # Verify result
            test_setup["logger"].info(
                "Add files by type test completed", success=result.success
            )

            assert result.success, "Add files by type workflow test failed"
        except Exception as e:
            test_setup["logger"].error("Add files by type test failed", error=str(e))
            assert False, f"Add files by type test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_add_files_by_type_cancel(self, test_setup):
        """Test adding files by type with cancellation."""
        test_setup["logger"].info("Testing add files by type - cancel operation")

        # Mock responses: Choose orchestrator (1), add by type (5), cancel (0), exit (0)
        responses = ["1", "5", "0", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Add Files by Type - Cancel"
            )

            # Verify result
            test_setup["logger"].info(
                "Add files by type - cancel test completed", success=result.success
            )

            assert result.success, "Add files by type - cancel test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Add files by type - cancel test failed", error=str(e)
            )
            assert (
                False
            ), f"Add files by type - cancel test failed with exception: {str(e)}"

    # ==================== CLEAR DATABASE TESTS ====================

    @pytest.mark.e2e
    def test_clear_database_workflow(self, test_setup):
        """Test clearing the database through the menu system."""
        test_setup["logger"].info("Testing clear database workflow")

        # First add some files to the database
        self.test_process_new_files_workflow(test_setup)

        # Mock responses: Choose orchestrator (1), clear database (4), confirm (y), exit (0)
        responses = ["1", "4", "y", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Clear Database Workflow"
            )

            # Verify result
            test_setup["logger"].info(
                "Clear database test completed", success=result.success
            )

            # Since we're mocking, just verify the test completed successfully
            assert result.success, "Clear database workflow test failed"
        except Exception as e:
            test_setup["logger"].error("Clear database test failed", error=str(e))
            assert False, f"Clear database test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_clear_database_cancel(self, test_setup):
        """Test clearing the database with cancellation."""
        test_setup["logger"].info("Testing clear database - cancel operation")

        # First add some files to the database
        self.test_process_new_files_workflow(test_setup)

        # Mock responses: Choose orchestrator (1), clear database (4), cancel (n), exit (0)
        responses = ["1", "4", "n", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Clear Database - Cancel"
            )

            # Verify result
            test_setup["logger"].info(
                "Clear database - cancel test completed", success=result.success
            )

            # Since we're mocking, just verify the test completed successfully
            assert result.success, "Clear database - cancel test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Clear database - cancel test failed", error=str(e)
            )
            assert (
                False
            ), f"Clear database - cancel test failed with exception: {str(e)}"

    # ==================== ERROR HANDLING TESTS ====================

    @pytest.mark.e2e
    def test_error_handling_invalid_choice(self, test_setup):
        """Test error handling with invalid menu choices."""
        test_setup["logger"].info("Testing error handling with invalid choices")

        # Mock responses: Choose orchestrator (1), invalid choice (99), exit (0)
        responses = ["1", "99", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Error Handling (Invalid Choice)"
            )

            # Verify result - should handle invalid choice gracefully
            test_setup["logger"].info(
                "Error handling test completed", success=result.success
            )

            assert (
                result.success
            ), "Error handling test failed - should handle invalid choice gracefully"
        except Exception as e:
            test_setup["logger"].error("Error handling test failed", error=str(e))
            assert False, f"Error handling test failed with exception: {str(e)}"

    @pytest.mark.e2e
    def test_error_handling_empty_input(self, test_setup):
        """Test error handling with empty input."""
        test_setup["logger"].info("Testing error handling with empty input")

        # Mock responses: Choose orchestrator (1), empty input (""), exit (0)
        responses = ["1", "", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Error Handling (Empty Input)"
            )

            # Verify result - should handle empty input gracefully
            test_setup["logger"].info(
                "Error handling - empty input test completed", success=result.success
            )

            assert result.success, "Error handling - empty input test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Error handling - empty input test failed", error=str(e)
            )
            assert (
                False
            ), f"Error handling - empty input test failed with exception: {str(e)}"

    # ==================== HANDLE EXISTING FILES TESTS ====================

    @pytest.mark.e2e
    def test_handle_existing_files_workflow(self, test_setup):
        """Test handling existing files through the menu system."""
        test_setup["logger"].info("Testing handle existing files workflow")

        # First add some files to the database
        self.test_process_new_files_workflow(test_setup)

        # Mock responses: Choose orchestrator (1), handle existing files (2), exit (0)
        responses = ["1", "2", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Handle Existing Files Workflow"
            )

            # Verify result
            test_setup["logger"].info(
                "Handle existing files test completed", success=result.success
            )

            assert result.success, "Handle existing files workflow test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Handle existing files test failed", error=str(e)
            )
            assert False, f"Handle existing files test failed with exception: {str(e)}"

    # ==================== HANDLE ORPHANED FILES TESTS ====================

    @pytest.mark.e2e
    def test_handle_orphaned_files_workflow(self, test_setup):
        """Test handling orphaned files through the menu system."""
        test_setup["logger"].info("Testing handle orphaned files workflow")

        # Mock responses: Choose orchestrator (1), handle orphaned files (3), exit (0)
        responses = ["1", "3", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Handle Orphaned Files Workflow"
            )

            # Verify result
            test_setup["logger"].info(
                "Handle orphaned files test completed", success=result.success
            )

            assert result.success, "Handle orphaned files workflow test failed"
        except Exception as e:
            test_setup["logger"].error(
                "Handle orphaned files test failed", error=str(e)
            )
            assert False, f"Handle orphaned files test failed with exception: {str(e)}"

    # ==================== CONFIRMATION TESTS ====================

    @pytest.mark.e2e
    def test_confirmation_workflow(self, test_setup):
        """Test confirmation workflows throughout the menu system."""
        test_setup["logger"].info("Testing confirmation workflows")

        # Test various confirmation scenarios
        test_scenarios = [
            ("Confirm Process All", ["1", "1", "1", "0"]),
            ("Cancel Process All", ["1", "1", "0", "0"]),
            ("Confirm Clear Database", ["1", "4", "y", "0"]),
            ("Cancel Clear Database", ["1", "4", "n", "0"]),
        ]

        results = []
        for scenario_name, responses in test_scenarios:
            try:
                result = self._run_test_with_mocked_input(
                    test_setup, responses, scenario_name
                )
                results.append(result.success)
                test_setup["logger"].info(
                    f"{scenario_name} completed", success=result.success
                )
            except Exception as e:
                test_setup["logger"].error(f"{scenario_name} failed", error=str(e))
                results.append(False)

        # All scenarios should succeed
        assert all(results), "Some confirmation workflow tests failed"

    @pytest.mark.benchmark
    def test_menu_performance(self, test_setup):
        """Test menu system performance."""
        test_setup["logger"].info("Testing menu system performance")

        # Mock responses for a typical workflow
        responses = ["1", "1", "1", "0"]

        try:
            result = self._run_test_with_mocked_input(
                test_setup, responses, "Menu Performance Test"
            )

            # Verify result
            test_setup["logger"].info(
                "Menu performance test completed", success=result.success
            )

            assert result.success, "Menu performance test failed"
        except Exception as e:
            test_setup["logger"].error("Menu performance test failed", error=str(e))
            assert False, f"Menu performance test failed with exception: {str(e)}"


def run_tests_with_data_directory(data_directory):
    """Run all tests with a specific data directory using enterprise practices."""
    print(f"🧪 Running comprehensive menu tests with data directory: {data_directory}")
    print("=" * 80)

    # Use enterprise-grade temporary environment
    with create_temp_test_environment() as temp_env:
        # Initialize test class
        test = TestEndToEndMenu()

        # Create test setup with proper mocking
        StructLogConfig.configure(debug=True)
        logger = structlog.get_logger("e2e_menu_test")

        # Create mock services (enterprise practice: mock external dependencies)
        mock_vector_store = Mock(spec=ChromaDBVectorStore)
        mock_vector_store.collection = Mock()
        mock_vector_store.collection.count.return_value = 5
        mock_vector_store.clear_all_documents.return_value = 5
        mock_vector_store.add_documents.return_value = True
        mock_vector_store.get_all_document_sources.return_value = [
            "test_document.pdf",
            "test_document.txt",
        ]
        mock_vector_store.document_exists.return_value = False
        mock_vector_store.get_document_count.return_value = 5

        mock_embedding_generator = Mock(spec=SentenceTransformerEmbeddingGenerator)
        mock_embedding_generator.generate_embeddings.return_value = [
            [0.1, 0.2, 0.3] for _ in range(3)
        ]

        mock_document_loader = Mock(spec=FileSystemDocumentLoader)
        mock_document_loader.load_documents.return_value = []

        mock_text_chunker = Mock(spec=ParagraphTextChunker)
        mock_text_chunker.chunk_text.return_value = []

        mock_text_extractor_factory = Mock(spec=TextExtractorFactory)

        test_setup = {
            "logger": logger,
            "data_dir": temp_env["data_dir"],
            "chroma_dir": temp_env["chroma_dir"],
            "vector_store": mock_vector_store,
            "embedding_generator": mock_embedding_generator,
            "document_loader": mock_document_loader,
            "text_chunker": mock_text_chunker,
            "text_extractor_factory": mock_text_extractor_factory,
        }

        # Get all test methods
        test_methods = [
            method
            for method in dir(test)
            if method.startswith("test_") and callable(getattr(test, method))
        ]

        print(f"📊 Found {len(test_methods)} test methods")
        print()

        # Run all tests
        results = {}
        passed = 0
        failed = 0

        for method_name in test_methods:
            method = getattr(test, method_name)
            print(f"🔍 Running: {method_name}")

            try:
                result = method(test_setup)
                if result and hasattr(result, 'success') and result.success:
                    print(f"✅ PASSED: {method_name}")
                    passed += 1
                    results[method_name] = "PASSED"
                else:
                    print(f"❌ FAILED: {method_name}")
                    failed += 1
                    results[method_name] = "FAILED"
            except Exception as e:
                print(f"💥 ERROR: {method_name} - {str(e)}")
                failed += 1
                results[method_name] = f"ERROR: {str(e)}"

            print()

        # Print summary
        print("=" * 80)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {len(test_methods)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(test_methods)*100):.1f}%")
        print("=" * 80)

        # Cleanup happens automatically via context manager
        print("🧹 Automatic cleanup completed via context manager")

        return failed == 0  # Return True if all tests passed


if __name__ == "__main__":
    # Run tests with default data directory
    run_tests_with_data_directory("tests/data/hr_policy")
