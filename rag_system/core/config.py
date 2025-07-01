"""
Configuration management for the RAG system.

This module provides centralized configuration using Pydantic settings
with environment variable support and validation.
"""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = Field(default="RAG System", description="Application name")
    app_version: str = Field(
        default="1.0.0",
        description="Application version",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Data settings
    data_directory: Path = Field(
        default=Path("data"),
        description="Directory containing documents to process",
    )
    supported_file_types: List[str] = Field(
        default=[".pdf", ".txt", ".docx", ".md", ".csv", ".xlsx"],
        description="Supported file types for processing",
    )

    # Vector store settings
    chroma_persist_directory: Path = Field(
        default=Path("./chroma_db"),
        description="ChromaDB persistence directory",
    )
    chroma_telemetry_enabled: bool = Field(
        default=False, description="Avoid sending telemetry events"
    )
    collection_name: str = Field(
        default="hr_policies",
        description="ChromaDB collection name",
    )

    # Embedding settings
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model name",
    )
    chunk_size: int = Field(
        default=30,
        description="Size of text chunks for processing",
    )
    chunk_overlap: int = Field(
        default=6,
        description="Overlap between text chunks",
    )
    # Adaptive chunking settings
    small_chunk_size: int = Field(
        default=300,
        description="Chunk size for small documents (characters)",
    )
    small_chunk_overlap: int = Field(
        default=50,
        description="Chunk overlap for small documents (characters)",
    )
    large_chunk_size: int = Field(
        default=1000,
        description="Chunk size for large documents (characters)",
    )
    large_chunk_overlap: int = Field(
        default=200,
        description="Chunk overlap for large documents (characters)",
    )
    chunk_size_threshold: int = Field(
        default=1000,
        description="Threshold (characters) to distinguish small vs large documents",
    )

    # LLM settings
    openai_api_key: Optional[str] = Field(
        default="none",
        description="OpenAI API key for LLM integration",
    )
    openai_model_name: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI model name",
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json",
        description="Log format (json or text)",
    )

    # UI settings
    streamlit_port: int = Field(default=8501, description="Streamlit UI port")

    @field_validator("chroma_persist_directory")
    def create_directories(cls, v):
        """Ensure Chroma directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
