#!/usr/bin/env python3
"""
Test runner script for menu functionality tests.
Allows testing with specific data directories or all available data directories.
Uses enterprise-grade practices with automatic cleanup.
"""
import argparse
import os
import sys
from pathlib import Path

# Add the tests directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from test_menu_functionality import TestEndToEndMenu, run_tests_with_data_directory


def list_available_data_directories():
    """List all available data directories for testing."""
    tests_data_dir = Path("tests/data")
    if not tests_data_dir.exists():
        print("No tests/data directory found.")
        return []

    data_dirs = []
    for item in tests_data_dir.iterdir():
        if item.is_dir():
            data_dirs.append(str(item))

    return data_dirs


def run_default_tests():
    """Run tests with default data directory using enterprise practices."""
    print("Testing with default data directory (creates temporary test files)")
    
    # Import the context manager for enterprise-grade testing
    from test_menu_functionality import create_temp_test_environment
    
    with create_temp_test_environment() as temp_env:
        # Initialize test class
        test = TestEndToEndMenu()
        
        # Create test setup
        import structlog
        from test_menu_functionality import StructLogConfig
        from unittest.mock import Mock
        from test_menu_functionality import (
            ChromaDBVectorStore, SentenceTransformerEmbeddingGenerator,
            FileSystemDocumentLoader, ParagraphTextChunker, TextExtractorFactory
        )
        
        StructLogConfig.configure(debug=True)
        logger = structlog.get_logger("default_test")
        
        # Create mock services
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
                else:
                    print(f"❌ FAILED: {method_name}")
                    failed += 1
            except Exception as e:
                print(f"💥 ERROR: {method_name} - {str(e)}")
                failed += 1
            
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
        
        return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Run menu functionality tests with different data directories"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Specific data directory to test (e.g., tests/data/hr_policy)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Test all available data directories"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available data directories"
    )
    parser.add_argument(
        "--default",
        action="store_true",
        help="Test with default data directory (creates temporary test files)",
    )

    args = parser.parse_args()

    if args.list:
        print("Available data directories:")
        data_dirs = list_available_data_directories()
        if data_dirs:
            for data_dir in data_dirs:
                print(f"  - {data_dir}")
        else:
            print("  No data directories found.")
        return

    all_passed = True

    if args.data_dir:
        # Test with specific data directory
        if os.path.exists(args.data_dir):
            print(f"Testing with data directory: {args.data_dir}")
            success = run_tests_with_data_directory(args.data_dir)
            all_passed = success
        else:
            print(f"Error: Data directory not found: {args.data_dir}")
            all_passed = False

    elif args.all:
        # Test with all available data directories
        data_dirs = list_available_data_directories()
        if not data_dirs:
            print("No data directories found to test.")
            return

        print(f"Testing with {len(data_dirs)} data directories:")
        for data_dir in data_dirs:
            print(f"\n{'='*80}")
            print(f"TESTING WITH DATA DIRECTORY: {data_dir}")
            print(f"{'='*80}")
            success = run_tests_with_data_directory(data_dir)
            if not success:
                all_passed = False

    elif args.default:
        # Test with default data directory using enterprise practices
        success = run_default_tests()
        all_passed = success

    else:
        # Default behavior: test with all available directories + default
        data_dirs = list_available_data_directories()

        # Test with available data directories
        for data_dir in data_dirs:
            print(f"\n{'='*80}")
            print(f"TESTING WITH DATA DIRECTORY: {data_dir}")
            print(f"{'='*80}")
            success = run_tests_with_data_directory(data_dir)
            if not success:
                all_passed = False

        # Also test with default data directory
        print(f"\n{'='*80}")
        print("TESTING WITH DEFAULT DATA DIRECTORY")
        print(f"{'='*80}")
        success = run_default_tests()
        if not success:
            all_passed = False

    print(f"\n🎯 OVERALL TESTING {'PASSED' if all_passed else 'FAILED'}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
