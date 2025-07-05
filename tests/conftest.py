"""
Shared pytest fixtures for the RAG system tests.

This module provides reusable fixtures that can be used across all test modules
to reduce code duplication and improve test maintainability.
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from rag_system.core.config import Settings


@pytest.fixture
def temp_dir() -> Any:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def settings() -> Any:
    """Create a Settings instance for tests."""
    return Settings()


@pytest.fixture
def test_data_dir(temp_dir: Any) -> Any:
    """Create a test data directory with sample files."""
    data_dir = temp_dir / "data"
    data_dir.mkdir()

    # Create test files
    (data_dir / "test.txt").write_text("Test content for text file")
    (data_dir / "test.pdf").write_text("PDF content for test")
    (data_dir / "ignored.py").write_text("Python code that should be ignored")
    (data_dir / "sample.md").write_text(
        "# Sample Markdown\n\nThis is a test markdown file."
    )

    return data_dir


@pytest.fixture
def sample_documents() -> Any:
    """Create sample Document objects for testing."""
    return [
        Document(
            page_content="This is a test document with some content. " * 10,
            metadata={"source": "test.txt", "file_type": ".txt"},
        ),
        Document(
            page_content="Another test document with different content. " * 8,
            metadata={"source": "test2.txt", "file_type": ".txt"},
        ),
        Document(
            page_content="Short document.",
            metadata={"source": "short.txt", "file_type": ".txt"},
        ),
    ]


@pytest.fixture
def mock_embeddings() -> Any:
    """Create mock embeddings for testing."""
    return [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.6, 0.7, 0.8, 0.9, 1.0],
        [0.11, 0.12, 0.13, 0.14, 0.15],
    ]


@pytest.fixture
def mock_embedding_function() -> Any:
    """Create a mock embedding function."""
    return Mock(
        return_value=[
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.6, 0.7, 0.8, 0.9, 1.0],
            [0.11, 0.12, 0.13, 0.14, 0.15],
        ]
    )


@pytest.fixture
def mock_chroma_collection() -> Any:
    """Create a mock ChromaDB collection."""
    collection = Mock()
    collection.add.return_value = None
    collection.query.return_value = {
        "documents": [["Test document content"]],
        "metadatas": [[{"source": "test.txt"}]],
        "distances": [[0.1]],
    }
    collection.count.return_value = 3
    return collection


@pytest.fixture
def mock_chroma_client() -> Any:
    """Create a mock ChromaDB client."""
    client = Mock()
    client.get_or_create_collection.return_value = Mock()
    return client


@pytest.fixture
def mock_huggingface_embeddings() -> Any:
    """Create a mock HuggingFace embeddings model."""
    model = Mock()
    model.embed_documents.return_value = [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.6, 0.7, 0.8, 0.9, 1.0],
        [0.11, 0.12, 0.13, 0.14, 0.15],
    ]
    return model


@pytest.fixture
def mock_huggingface_embeddings_model() -> Any:
    """Create a mock HuggingFace embeddings model for testing."""
    model = Mock()
    model.embed_documents.return_value = [
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.6, 0.7, 0.8, 0.9, 1.0],
        [0.11, 0.12, 0.13, 0.14, 0.15],
    ]
    return model


@pytest.fixture
def mock_openai_llm() -> Any:
    """Create a mock OpenAI LLM."""
    llm = Mock()
    llm.invoke.return_value.content = "This is a mock LLM response."
    return llm


@pytest.fixture
def mock_retrieval_results() -> Any:
    """Create mock retrieval results for RAG testing."""
    return [
        (
            Document(
                page_content="Relevant document 1",
                metadata={"source": "doc1.txt"},
            ),
            0.8,
        ),
        (
            Document(
                page_content="Relevant document 2",
                metadata={"source": "doc2.txt"},
            ),
            0.6,
        ),
        (
            Document(
                page_content="Less relevant document",
                metadata={"source": "doc3.txt"},
            ),
            0.3,
        ),
    ]


@pytest.fixture
def settings_with_openai_key() -> Any:
    """Create Settings with OpenAI API key for LLM tests."""
    # Use environment variable approach since Settings is frozen
    import os

    original_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    try:
        return Settings()
    finally:
        if original_key is not None:
            os.environ["OPENAI_API_KEY"] = original_key
        else:
            os.environ.pop("OPENAI_API_KEY", None)


@pytest.fixture
def settings_without_openai_key() -> Any:
    """Create Settings without OpenAI API key for testing error cases."""
    # Create a test-specific Settings class that doesn't load from .env
    from pydantic_settings import SettingsConfigDict

    class TestSettings(Settings):
        """Test settings that don't load from .env file."""

        model_config = SettingsConfigDict(
            env_file=None,  # Disable .env file loading
            populate_by_name=True,
            frozen=True,
        )

    # Create settings with clean environment
    import os
    from unittest.mock import patch

    original_env = dict(os.environ)
    clean_env = {
        k: v
        for k, v in original_env.items()
        if not k.upper().startswith("OPENAI")
    }

    with patch.dict(os.environ, clean_env, clear=True):
        settings = TestSettings()
        assert settings.openai_api_key is None
        return settings


@pytest.fixture
def blank_env_file(temp_dir: Any) -> Any:
    """Create a blank .env file for isolated environment testing."""
    env_path = temp_dir / "blank.env"
    env_path.write_text("")
    return env_path


@pytest.fixture
def test_env_file(temp_dir: Any) -> Any:
    """Create a test .env file with various settings."""
    env_content = """
    APP_NAME=TestApp
    LOG_LEVEL=DEBUG
    CHUNK_SIZE=123
    CHUNK_OVERLAP=7
    CHROMA_PERSIST_DIRECTORY=./test_chroma
    CHROMA_TELEMETRY_ENABLED=true
    EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
    OPENAI_API_KEY=test-key
    OPENAI_MODEL_NAME=gpt-4
    """.strip()

    env_path = temp_dir / "test.env"
    env_path.write_text(env_content)
    return env_path


@pytest.fixture
def mock_text_loader() -> Any:
    """Create a mock text loader for document loading tests."""
    loader = Mock()
    doc = Mock()
    doc.page_content = "Test content for text file"
    doc.metadata = {}
    loader.load.return_value = [doc]
    return loader


@pytest.fixture
def rag_system_instance(settings: Any) -> Any:
    """Create a RAGSystem instance for testing."""
    from rag_system.rag_system import RAGSystem

    return RAGSystem(settings=settings)


@pytest.fixture
def text_processor_instance(settings: Any) -> Any:
    """Create a TextProcessor instance for testing."""
    from rag_system.ingestion.text_processor import TextProcessor

    return TextProcessor(
        settings=settings,
        embedding_model_name="all-MiniLM-L6-v2",
        chunk_size=100,
        chunk_overlap=20,
    )


@pytest.fixture
def document_loader_instance(settings: Any, test_data_dir: Any) -> Any:
    """Create a DocumentLoader instance for testing."""
    from rag_system.ingestion.document_loader import DocumentLoader

    return DocumentLoader(settings, data_directory=test_data_dir)
