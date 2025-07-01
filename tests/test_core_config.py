"""
Tests for the configuration module.

This module tests the Pydantic-based configuration system with
environment variable support and validation.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from rag_system.core.config import Settings


class TestSettings:
    """Test cases for the Settings class."""

    def test_default_settings(self):
        """Test that default settings are correctly set."""
        settings = Settings()

        assert settings.app_name == "RAG System"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.data_directory == Path("data")
        assert ".pdf" in settings.supported_file_types
        assert ".txt" in settings.supported_file_types
        assert settings.embedding_model_name == "all-MiniLM-L6-v2"
        assert settings.chunk_size == 1000
        assert settings.chunk_overlap == 200
        assert settings.log_level == "INFO"

    def test_custom_settings(self):
        """Test that custom settings can be set."""
        settings = Settings(
            app_name="Custom RAG",
            debug=True,
            chunk_size=500,
            log_level="DEBUG",
        )

        assert settings.app_name == "Custom RAG"
        assert settings.debug is True
        assert settings.chunk_size == 500
        assert settings.log_level == "DEBUG"

    def test_environment_variables(self):
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Env RAG",
                "DEBUG": "true",
                "CHUNK_SIZE": "750",
                "LOG_LEVEL": "WARNING",
            },
        ):
            settings = Settings()

            assert settings.app_name == "Env RAG"
            assert settings.debug is True
            assert settings.chunk_size == 750
            assert settings.log_level == "WARNING"

    def test_directory_creation(self):
        """Test that directories are created automatically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "test_data"
            chroma_dir = Path(temp_dir) / "test_chroma"

            Settings(
                data_directory=data_dir,
                chroma_persist_directory=chroma_dir,
            )

            assert data_dir.exists()
            assert chroma_dir.exists()

    def test_log_level_validation(self):
        """Test that invalid log levels raise validation errors."""
        with pytest.raises(ValueError, match="Log level must be one of"):
            Settings(log_level="INVALID")

    def test_supported_file_types(self):
        """Test that supported file types are correctly configured."""
        settings = Settings()

        expected_types = [".pdf", ".txt", ".docx", ".md", ".csv", ".xlsx"]
        assert all(ft in settings.supported_file_types for ft in expected_types)

    def test_optional_openai_key(self):
        """Test that OpenAI API key is optional."""
        settings = Settings()
        assert settings.openai_api_key is None

        # Test with API key
        settings_with_key = Settings(openai_api_key="test-key")
        assert settings_with_key.openai_api_key == "test-key"

    def test_chroma_settings(self):
        """Test ChromaDB-specific settings."""
        settings = Settings()

        assert settings.chroma_persist_directory == Path("./chroma_db")
        assert settings.collection_name == "hr_policies"

    def test_embedding_settings(self):
        """Test embedding model settings."""
        settings = Settings()

        assert settings.embedding_model_name == "all-MiniLM-L6-v2"
        assert settings.chunk_size == 1000
        assert settings.chunk_overlap == 200

    def test_ui_settings(self):
        """Test UI-related settings."""
        settings = Settings()

        assert settings.streamlit_port == 8501
        assert settings.log_format == "json"

    def test_settings_immutability(self):
        """Test that settings are properly validated and immutable."""
        settings = Settings()

        # Test that we can't set invalid values after creation
        with pytest.raises(AttributeError):
            settings.app_name = "New Name"

    def test_settings_repr(self):
        """Test that settings have a proper string representation."""
        settings = Settings()
        repr_str = repr(settings)

        assert "Settings" in repr_str
        assert "app_name" in repr_str
        assert "RAG System" in repr_str

    def test_document_source(self):
        """Test that document source is correctly set."""
        settings = Settings()
        documents = [
            {"metadata": {"source": str(settings.data_directory / "test.txt")}}
        ]
        assert documents[0].metadata["source"] == str(
            settings.data_directory / "test.txt"
        )
