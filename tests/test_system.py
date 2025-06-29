import logging
import os
import sys

from typing import List

from src.chroma.vector_store import ChromaDBVectorStore
from src.embeddings.embedding_generator import SentenceTransformerEmbeddingGenerator
from src.ingestion.commands.process_files_command import ProcessNewFilesCommand
from src.ingestion.core.enums import BulkActionChoice, FileActionChoice, FileType
from src.ingestion.core.interfaces.text_chunker import TextChunker
from src.ingestion.services.document_loader import FileSystemDocumentLoader
from src.ingestion.services.text_chunker import ParagraphTextChunker
from src.ingestion.services.text_extractor_factory import TextExtractorFactory
from src.menu.commands.back_command import BackCommand
from src.menu.commands.exit_command import ExitCommand
from src.menu.core.enums import CommandType, MenuAction, MenuChoice
from src.menu.core.menu_command import MenuCommand, CommandContext, CommandResult
from src.menu.core.menu_registry import MenuRegistry


def test_menu_system_imports():
    """Test that menu system components can be imported."""

    # Test that imports worked
    assert MenuAction is not None
    assert MenuChoice is not None
    assert CommandType is not None
    assert MenuCommand is not None
    assert CommandContext is not None
    assert CommandResult is not None
    assert MenuRegistry is not None
    assert BackCommand is not None
    assert ExitCommand is not None


def test_menu_system_instances():
    """Test that menu system components can be instantiated."""
    # Test creating instances
    registry = MenuRegistry()
    back_cmd = BackCommand()
    exit_cmd = ExitCommand()

    assert registry is not None
    assert back_cmd is not None
    assert exit_cmd is not None


def test_ingestion_system_imports():
    """Test that ingestion system components can be imported."""
    # Test that imports worked
    assert FileType is not None
    assert BulkActionChoice is not None
    assert FileActionChoice is not None
    assert ProcessNewFilesCommand is not None


def test_ingestion_system_instances():
    """Test that ingestion system components can be instantiated."""
    # Test creating instances
    cmd = ProcessNewFilesCommand()
    assert cmd is not None


def test_logging_module_exists():
    """Test that the logging module exists."""
    logging_path = os.path.join("src", "logutils", "logger.py")
    assert os.path.exists(logging_path), "Logger module not found at {logging_path}"


def test_embedding_generator_import():
    """Test that embedding generator can be imported."""
    assert SentenceTransformerEmbeddingGenerator is not None


def test_vector_store_import():
    """Test that vector store can be imported."""
    assert ChromaDBVectorStore is not None


def test_core_services_imports():
    """Test that all core services can be imported."""
    assert FileSystemDocumentLoader is not None
    assert ParagraphTextChunker is not None
    assert TextExtractorFactory is not None
    assert SentenceTransformerEmbeddingGenerator is not None
    assert ChromaDBVectorStore is not None
    assert TextChunker is not None
