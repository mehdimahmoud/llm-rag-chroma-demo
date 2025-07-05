"""
Tests for the configuration module.

This module tests the Pydantic-based configuration system with
environment variable support and validation.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic_settings import SettingsConfigDict

from rag_system.core.config import Settings


class TestSettings:
    """Test cases for the Settings class."""

    def test_default_settings(self, settings: Settings) -> None:
        """Test that default settings are correctly set."""
        assert settings.app_name == "RAG System"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.data_directory == Path("data")
        assert ".pdf" in settings.supported_file_types
        assert ".txt" in settings.supported_file_types
        assert settings.embedding_model_name == "all-MiniLM-L6-v2"
        assert settings.small_chunk_size == 300
        assert settings.small_chunk_overlap == 50
        assert settings.large_chunk_size == 1000
        assert settings.large_chunk_overlap == 200
        assert settings.chunk_size_threshold == 1000
        assert settings.log_level == "INFO"

    def test_custom_settings(self) -> None:
        """Test that custom settings can be set."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Custom RAG",
                "DEBUG": "true",
                "CHUNK_SIZE": "500",
                "LOG_LEVEL": "DEBUG",
            },
        ):
            settings = Settings()
            assert settings.app_name == "Custom RAG"
            assert settings.debug is True
            assert settings.chunk_size == 500
            assert settings.log_level == "DEBUG"

    def test_environment_variables(self) -> None:
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

    def test_directory_creation(self, temp_dir: Path) -> None:
        """Test that directories are created automatically."""
        data_dir = temp_dir / "test_data"
        chroma_dir = temp_dir / "test_chroma"
        with patch.dict(
            os.environ,
            {
                "DATA_DIRECTORY": str(data_dir),
                "CHROMA_PERSIST_DIRECTORY": str(chroma_dir),
            },
        ):
            Settings()
            assert data_dir.exists()
            assert chroma_dir.exists()

    def test_log_level_validation(self) -> None:
        """Test that invalid log levels raise validation errors."""
        with pytest.raises(ValueError, match="Log level must be one of"):
            Settings(LOG_LEVEL="INVALID")  # type: ignore

    def test_supported_file_types(self, settings: Settings) -> None:
        """Test that supported file types are correctly configured."""
        expected_types = [".pdf", ".txt", ".docx", ".md", ".csv", ".xlsx"]
        for ft in expected_types:
            assert ft in settings.supported_file_types

    def test_optional_openai_key(self, blank_env_file: Path) -> None:
        """
        Test that OpenAI API key is optional,
        using a blank temp .env for isolation.
        """

        class TestEnvSettings(Settings):
            openai_api_key: str | None = None
            model_config = SettingsConfigDict(
                env_file=str(blank_env_file),
                populate_by_name=True,
                frozen=True,
            )

        with patch.dict(os.environ, {}, clear=True):
            settings = TestEnvSettings()
            assert settings.openai_api_key is None
        # Test with API key set explicitly
        settings_with_key = TestEnvSettings(openai_api_key="test-key")
        assert settings_with_key.openai_api_key == "test-key"

    def test_chroma_settings(self, settings: Settings) -> None:
        """Test ChromaDB-specific settings."""
        assert settings.chroma_persist_directory == Path("chroma_db")
        assert settings.collection_name == "hr_policies"

    def test_embedding_settings(self, settings: Settings) -> None:
        """Test embedding model settings."""
        assert settings.embedding_model_name == "all-MiniLM-L6-v2"
        assert settings.small_chunk_size == 300
        assert settings.small_chunk_overlap == 50
        assert settings.large_chunk_size == 1000
        assert settings.large_chunk_overlap == 200
        assert settings.chunk_size_threshold == 1000

    def test_ui_settings(self, settings: Settings) -> None:
        """Test UI-related settings."""
        assert settings.streamlit_port == 8501
        assert settings.log_format == "text"

    def test_settings_immutability(self, settings: Settings) -> None:
        """Test that settings are properly validated and immutable (frozen)."""
        from pydantic_core import ValidationError

        # Test that we can't set invalid values after creation
        with pytest.raises(ValidationError):
            settings.app_name = "New Name"

    def test_settings_repr(self, settings: Settings) -> None:
        """Test that settings have a proper string representation."""
        repr_str = repr(settings)

        assert "Settings" in repr_str
        assert "app_name" in repr_str
        assert "RAG System" in repr_str

    def test_document_source(self, settings: Settings) -> None:
        """Test that document source is correctly set."""
        test_file_path = str(settings.data_directory / "test.txt")
        documents = [{"metadata": {"source": test_file_path}}]
        expected_source = str(settings.data_directory / "test.txt")
        assert documents[0]["metadata"]["source"] == expected_source

    def test_env_to_settings_mapping(
        self, test_env_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that all .env variables are mapped to Settings fields."""
        monkeypatch.chdir(test_env_file.parent)

        # Clear environment variables to ensure test.env file is used
        for var in [
            "APP_NAME",
            "LOG_LEVEL",
            "CHUNK_SIZE",
            "CHUNK_OVERLAP",
            "CHROMA_PERSIST_DIRECTORY",
            "CHROMA_TELEMETRY_ENABLED",
            "EMBEDDING_MODEL_NAME",
            "OPENAI_API_KEY",
            "OPENAI_MODEL_NAME",
        ]:
            monkeypatch.delenv(var, raising=False)

        class TestEnvSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=str(test_env_file), populate_by_name=True, frozen=True
            )

        TestEnvSettings.model_rebuild(force=True)
        settings = TestEnvSettings()
        assert settings.app_name == "TestApp"
        assert settings.log_level == "DEBUG"
        assert settings.chunk_size == 123
        assert settings.chunk_overlap == 7
        assert settings.chroma_persist_directory == Path("./tests/test_chroma")
        assert settings.chroma_telemetry_enabled is True
        assert settings.embedding_model_name == "all-MiniLM-L6-v2"
        assert settings.openai_api_key == "test-key"
        assert settings.openai_model_name == "gpt-4"
