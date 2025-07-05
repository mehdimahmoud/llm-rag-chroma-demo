"""
Configuration management for the RAG system.

This module provides centralized configuration using Pydantic settings
with environment variable support and validation.
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env", populate_by_name=True, frozen=True
    )

    # Application settings
    app_name: Annotated[str, Field(alias="APP_NAME")] = "RAG System"
    app_version: Annotated[str, Field(alias="APP_VERSION")] = "1.0.0"
    debug: Annotated[bool, Field(alias="DEBUG")] = False

    # Data settings
    data_directory: Annotated[Path, Field(alias="DATA_DIRECTORY")] = Path(
        "data"
    )
    supported_file_types: Annotated[
        list[str], Field(alias="SUPPORTED_FILE_TYPES")
    ] = [".pdf", ".txt", ".docx", ".md", ".csv", ".xlsx"]

    # Vector store settings
    chroma_persist_directory: Annotated[
        Path, Field(alias="CHROMA_PERSIST_DIRECTORY")
    ] = Path("chroma")
    chroma_telemetry_enabled: Annotated[
        bool, Field(alias="CHROMA_TELEMETRY_ENABLED")
    ] = True
    collection_name: Annotated[str, Field(alias="COLLECTION_NAME")] = (
        "hr_policies"
    )

    # Embedding settings
    embedding_model_name: Annotated[
        str, Field(alias="EMBEDDING_MODEL_NAME")
    ] = "all-MiniLM-L6-v2"
    chunk_size: Annotated[int, Field(alias="CHUNK_SIZE")] = 30
    chunk_overlap: Annotated[int, Field(alias="CHUNK_OVERLAP")] = 0
    # Adaptive chunking settings
    small_chunk_size: Annotated[int, Field(alias="SMALL_CHUNK_SIZE")] = 300
    small_chunk_overlap: Annotated[int, Field(alias="SMALL_CHUNK_OVERLAP")] = (
        50
    )
    large_chunk_size: Annotated[int, Field(alias="LARGE_CHUNK_SIZE")] = 1000
    large_chunk_overlap: Annotated[int, Field(alias="LARGE_CHUNK_OVERLAP")] = (
        200
    )
    chunk_size_threshold: Annotated[
        int, Field(alias="CHUNK_SIZE_THRESHOLD")
    ] = 1000

    # LLM settings
    openai_api_key: Annotated[str | None, Field(alias="OPENAI_API_KEY")] = None
    openai_model_name: Annotated[str, Field(alias="OPENAI_MODEL_NAME")] = (
        "gpt-4o-mini"
    )

    # Logging settings
    log_level: Annotated[str, Field(alias="LOG_LEVEL")] = "INFO"
    log_format: Annotated[str, Field(alias="LOG_FORMAT")] = "text"

    # UI settings
    streamlit_port: Annotated[int, Field(alias="STREAMLIT_PORT")] = 8501

    @field_validator("chroma_persist_directory")
    def create_directories(cls, v: str | Path) -> Path:
        """Ensure Chroma directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator("data_directory")
    def create_data_directory(cls, v: str | Path) -> Path:
        """Ensure data directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
