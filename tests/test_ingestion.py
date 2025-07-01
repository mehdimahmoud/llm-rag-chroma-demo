"""
Tests for the ingestion components.

This module tests document loading, text processing, and vector storage
functionality with proper mocking and isolation.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from rag_system.ingestion.document_loader import DocumentLoader
from rag_system.ingestion.text_processor import TextProcessor
from rag_system.ingestion.vector_store import VectorStore


class TestDocumentLoader:
    """Test cases for the DocumentLoader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()

        # Create test files
        (self.data_dir / "test.txt").write_text("Test content")
        (self.data_dir / "test.pdf").write_text("PDF content")
        (self.data_dir / "ignored.py").write_text("Python code")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test DocumentLoader initialization."""
        loader = DocumentLoader(self.data_dir)

        assert loader.data_directory == self.data_dir
        assert ".pdf" in loader.supported_types
        assert ".txt" in loader.supported_types
        assert ".py" not in loader.supported_types

    def test_get_supported_files(self):
        """Test getting supported files."""
        loader = DocumentLoader(self.data_dir)
        files = loader.get_supported_files()

        file_names = [f.name for f in files]
        assert "test.txt" in file_names
        assert "test.pdf" in file_names
        assert "ignored.py" not in file_names

    @patch("rag_system.ingestion.document_loader.TextLoader")
    def test_load_document_txt(self, mock_loader_class):
        """Test loading a text document."""
        # Mock the loader
        mock_loader = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {}
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        loader = DocumentLoader(self.data_dir)
        documents = loader.load_document(self.data_dir / "test.txt")

        assert len(documents) == 1
        assert documents[0].page_content == "Test content"
        assert documents[0].metadata["source"] == str(self.data_dir / "test.txt")
        assert documents[0].metadata["file_type"] == ".txt"

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file."""
        loader = DocumentLoader(self.data_dir)

        with pytest.raises(FileNotFoundError):
            loader.load_document(self.data_dir / "nonexistent.txt")

    def test_load_unsupported_file_type(self):
        """Test loading an unsupported file type."""
        loader = DocumentLoader(self.data_dir)

        with pytest.raises(ValueError, match="Unsupported file type"):
            loader.load_document(self.data_dir / "ignored.py")

    def test_get_file_type_summary(self):
        """Test getting file type summary."""
        loader = DocumentLoader(self.data_dir)
        summary = loader.get_file_type_summary()

        assert summary[".txt"] == 1
        assert summary[".pdf"] == 1


class TestTextProcessor:
    """Test cases for the TextProcessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TextProcessor(
            embedding_model_name="all-MiniLM-L6-v2",
            chunk_size=100,
            chunk_overlap=20,
        )

    @patch("rag_system.ingestion.text_processor.SentenceTransformer")
    def test_initialization(self, mock_sentence_transformer):
        """Test TextProcessor initialization."""
        processor = TextProcessor()

        assert processor.embedding_model_name == "all-MiniLM-L6-v2"
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200
        assert processor.text_splitter is not None

    def test_chunk_documents(self):
        """Test document chunking."""
        from langchain_core.documents import Document

        # Create test documents
        docs = [
            Document(
                page_content=("This is a test document with some content. " * 10),
                metadata={"source": "test.txt"},
            )
        ]

        chunked_docs = self.processor.chunk_documents(docs)

        assert len(chunked_docs) > 1  # Should be chunked
        assert all(isinstance(doc, Document) for doc in chunked_docs)
        assert all(doc.metadata["source"] == "test.txt" for doc in chunked_docs)

    def test_chunk_empty_documents(self):
        """Test chunking empty document list."""
        chunked_docs = self.processor.chunk_documents([])
        assert chunked_docs == []

    @patch("rag_system.ingestion.text_processor.SentenceTransformer")
    def test_generate_embeddings(self, mock_sentence_transformer):
        """Test embedding generation."""
        # Mock the embedding model
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_sentence_transformer.return_value = mock_model

        processor = TextProcessor()
        texts = ["Hello world", "Test text"]
        embeddings = processor.generate_embeddings(texts)

        assert len(embeddings) == 2
        assert len(embeddings[0]) == 3
        assert len(embeddings[1]) == 3

    def test_generate_embeddings_empty(self):
        """Test generating embeddings for empty text list."""
        embeddings = self.processor.generate_embeddings([])
        assert embeddings == []

    def test_process_documents(self):
        """Test complete document processing."""
        from langchain_core.documents import Document

        docs = [
            Document(
                page_content="Test content for processing. " * 5,
                metadata={"source": "test.txt"},
            )
        ]

        chunked_docs, embeddings = self.processor.process_documents(docs)

        assert len(chunked_docs) > 0
        assert len(embeddings) > 0
        assert len(chunked_docs) == len(embeddings)


class TestVectorStore:
    """Test cases for the VectorStore class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.persist_dir = Path(self.temp_dir) / "chroma"

        # Mock embedding function
        self.mock_embedding_function = Mock(
            return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("rag_system.ingestion.vector_store.chromadb")
    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_initialization(self, mock_chroma, mock_chromadb):
        """Test VectorStore initialization."""
        # Mock ChromaDB client
        mock_client = Mock()
        mock_chromadb.PersistentClient.return_value = mock_client

        # Mock Chroma wrapper
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(
            persist_directory=str(self.persist_dir),
            collection_name="test_collection",
            embedding_function=self.mock_embedding_function,
        )

        assert vector_store.persist_directory == str(self.persist_dir)
        assert vector_store.collection_name == "test_collection"
        assert vector_store.embedding_function == self.mock_embedding_function

    @patch("rag_system.ingestion.vector_store.chromadb")
    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_add_documents(self, mock_chroma, mock_chromadb):
        """Test adding documents to vector store."""
        from langchain_core.documents import Document

        # Mock ChromaDB client
        mock_client = Mock()
        mock_chromadb.PersistentClient.return_value = mock_client

        # Mock Chroma wrapper
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(
            persist_directory=str(self.persist_dir),
            collection_name="test_collection",
            embedding_function=self.mock_embedding_function,
        )

        # Test documents
        docs = [
            Document(
                page_content="Test content 1",
                metadata={"source": "test1.txt"},
            ),
            Document(
                page_content="Test content 2",
                metadata={"source": "test2.txt"},
            ),
        ]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]

        doc_ids = vector_store.add_documents(docs, embeddings)

        assert len(doc_ids) == 2
        mock_chroma_instance.add_documents.assert_called_once()

    @patch("rag_system.ingestion.vector_store.chromadb")
    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_similarity_search(self, mock_chroma, mock_chromadb):
        """Test similarity search."""
        from langchain_core.documents import Document

        # Mock ChromaDB client
        mock_client = Mock()
        mock_chromadb.PersistentClient.return_value = mock_client

        # Mock Chroma wrapper
        mock_chroma_instance = Mock()
        mock_doc = Document(
            page_content="Test result",
            metadata={"source": "test.txt"},
        )
        mock_chroma_instance.similarity_search.return_value = [mock_doc]
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(
            persist_directory=str(self.persist_dir),
            collection_name="test_collection",
            embedding_function=self.mock_embedding_function,
        )

        results = vector_store.similarity_search("test query", k=2)

        assert len(results) == 1
        assert results[0].page_content == "Test result"
        mock_chroma_instance.similarity_search.assert_called_once()

    @patch("rag_system.ingestion.vector_store.chromadb")
    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_get_collection_stats(self, mock_chroma, mock_chromadb):
        """Test getting collection statistics."""
        # Mock ChromaDB client
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_client.get_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_client

        # Mock Chroma wrapper
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(
            persist_directory=str(self.persist_dir),
            collection_name="test_collection",
            embedding_function=self.mock_embedding_function,
        )

        stats = vector_store.get_collection_stats()

        assert stats["collection_name"] == "test_collection"
        assert stats["document_count"] == 42
        assert stats["persist_directory"] == str(self.persist_dir)

    def test_add_documents_mismatch(self):
        """Test that adding documents with mismatched
        embeddings raises error."""
        from langchain_core.documents import Document

        with patch("rag_system.ingestion.vector_store.chromadb"):
            with patch("rag_system.ingestion.vector_store.Chroma"):
                vector_store = VectorStore(
                    persist_directory=str(self.persist_dir),
                    collection_name="test_collection",
                    embedding_function=self.mock_embedding_function,
                )

                docs = [
                    Document(
                        page_content="Test",
                        metadata={},
                    )
                ]
                embeddings = [[0.1, 0.2], [0.3, 0.4]]  # Mismatched count

                with pytest.raises(
                    ValueError,
                    match="Number of documents must match",
                ):
                    vector_store.add_documents(docs, embeddings)
