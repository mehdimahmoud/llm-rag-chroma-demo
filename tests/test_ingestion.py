"""
Tests for the ingestion components.

This module tests document loading, text processing, and vector storage
functionality with proper mocking and isolation.
"""

from unittest.mock import Mock, patch

import pytest

from rag_system.ingestion.document_loader import DocumentLoader
from rag_system.ingestion.text_processor import TextProcessor
from rag_system.ingestion.vector_store import VectorStore
from rag_system.rag_system import RAGSystem, PromptBuilder
from rag_system.core.config import Settings
from langchain_core.documents import Document


class TestDocumentLoader:
    """Test cases for the DocumentLoader class."""

    def test_initialization(self, settings, test_data_dir):
        """Test DocumentLoader initialization."""
        loader = DocumentLoader(settings, data_directory=test_data_dir)

        assert loader.data_directory == test_data_dir
        assert ".pdf" in loader.supported_types
        assert ".txt" in loader.supported_types
        assert ".py" not in loader.supported_types

    def test_get_supported_files(self, settings, test_data_dir):
        """Test getting supported files."""
        loader = DocumentLoader(settings, data_directory=test_data_dir)
        files = loader.get_supported_files()

        file_names = [f.name for f in files]
        assert "test.txt" in file_names
        assert "test.pdf" in file_names
        assert "sample.md" in file_names
        assert "ignored.py" not in file_names

    @patch("rag_system.ingestion.document_loader.TextLoader")
    def test_load_document_txt(self, mock_loader_class, settings, test_data_dir, mock_text_loader):
        """Test loading a text document."""
        # Mock the loader
        mock_loader_class.return_value = mock_text_loader

        loader = DocumentLoader(settings, data_directory=test_data_dir)
        documents = loader.load_document(test_data_dir / "test.txt")

        assert len(documents) == 1
        assert documents[0].page_content == "Test content for text file"
        assert documents[0].metadata["source"] == str(test_data_dir / "test.txt")
        assert documents[0].metadata["file_type"] == ".txt"

    def test_load_nonexistent_file(self, settings, test_data_dir):
        """Test loading a non-existent file."""
        loader = DocumentLoader(settings, data_directory=test_data_dir)

        with pytest.raises(FileNotFoundError):
            loader.load_document(test_data_dir / "nonexistent.txt")

    def test_load_unsupported_file_type(self, settings, test_data_dir):
        """Test loading an unsupported file type."""
        loader = DocumentLoader(settings, data_directory=test_data_dir)

        with pytest.raises(ValueError, match="Unsupported file type"):
            loader.load_document(test_data_dir / "ignored.py")

    def test_get_file_type_summary(self, settings, test_data_dir):
        """Test getting file type summary."""
        loader = DocumentLoader(settings, data_directory=test_data_dir)
        summary = loader.get_file_type_summary()

        assert summary[".txt"] == 1
        assert summary[".pdf"] == 1
        assert summary[".md"] == 1


class TestTextProcessor:
    """Test cases for the TextProcessor class."""

    def test_initialization(self, settings):
        """Test TextProcessor initialization."""
        processor = TextProcessor(settings=settings)

        assert processor.embedding_model_name == "all-MiniLM-L6-v2"

    def test_chunk_documents(self, text_processor_instance, sample_documents):
        """Test document chunking."""
        chunked_docs = text_processor_instance.chunk_documents(sample_documents)

        assert len(chunked_docs) > 1  # Should be chunked
        assert all(isinstance(doc, Document) for doc in chunked_docs)
        assert all(doc.metadata["source"] in ["test.txt", "test2.txt", "short.txt"] for doc in chunked_docs)

    def test_chunk_empty_documents(self, text_processor_instance):
        """Test chunking empty document list."""
        chunked_docs = text_processor_instance.chunk_documents([])
        assert chunked_docs == []

    @patch("rag_system.ingestion.text_processor.HuggingFaceEmbeddings")
    def test_generate_embeddings(self, mock_huggingface_embeddings, settings):
        """Test embedding generation."""
        # Mock the HuggingFaceEmbeddings class and its embed_documents method
        mock_embeddings_instance = Mock()
        mock_embeddings_instance.embed_documents.return_value = [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.6, 0.7, 0.8, 0.9, 1.0]
        ]
        mock_huggingface_embeddings.return_value = mock_embeddings_instance

        processor = TextProcessor(settings=settings)
        texts = ["Hello world", "Test text"]
        embeddings = processor.generate_embeddings(texts)

        assert len(embeddings) == 2
        assert len(embeddings[0]) == 5
        assert len(embeddings[1]) == 5
        # Verify the actual method was called
        mock_embeddings_instance.embed_documents.assert_called_once_with(texts)

    def test_generate_embeddings_empty(self, text_processor_instance):
        """Test generating embeddings for empty text list."""
        embeddings = text_processor_instance.generate_embeddings([])
        assert embeddings == []

    def test_process_documents(self, text_processor_instance, sample_documents):
        """Test complete document processing."""
        chunked_docs, embeddings = text_processor_instance.process_documents(sample_documents)

        assert len(chunked_docs) > 0
        assert len(embeddings) > 0
        assert len(chunked_docs) == len(embeddings)


class TestVectorStore:
    """Test cases for the VectorStore class."""

    @patch("rag_system.ingestion.vector_store.chromadb")
    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_initialization(self, mock_chroma, mock_chromadb, settings, mock_embedding_function):
        """Test VectorStore initialization."""
        # Mock ChromaDB components
        mock_client = Mock()
        mock_collection = Mock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        vector_store = VectorStore(settings, embedding_function=mock_embedding_function)

        assert vector_store.embedding_function == mock_embedding_function
        assert vector_store.collection_name == settings.collection_name
        mock_chromadb.PersistentClient.assert_called_once()

    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_add_documents(self, mock_chroma, settings, mock_embedding_function, sample_documents, mock_embeddings):
        """Test adding documents to vector store."""
        # Mock the LangChain Chroma wrapper
        mock_chroma_instance = Mock()
        mock_chroma_instance.add_documents.return_value = ["doc_0_123", "doc_1_456", "doc_2_789"]
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(settings, embedding_function=mock_embedding_function)
        doc_ids = vector_store.add_documents(sample_documents, mock_embeddings)

        assert len(doc_ids) == len(sample_documents)
        # Verify the actual LangChain method was called with documents
        mock_chroma_instance.add_documents.assert_called_once()
        call_args = mock_chroma_instance.add_documents.call_args
        assert call_args[1]['documents'] == sample_documents

    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_similarity_search(self, mock_chroma, settings, mock_embedding_function):
        """Test similarity search."""
        # Mock the LangChain Chroma wrapper
        mock_chroma_instance = Mock()
        expected_results = [
            Document(page_content="Test document content", metadata={"source": "test.txt"})
        ]
        mock_chroma_instance.similarity_search.return_value = expected_results
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(settings, embedding_function=mock_embedding_function)
        results = vector_store.similarity_search("test query", k=1)

        assert len(results) == 1
        assert isinstance(results[0], Document)
        # Verify the actual LangChain method was called
        mock_chroma_instance.similarity_search.assert_called_once_with(
            query="test query", k=1, filter=None
        )

    @patch("rag_system.ingestion.vector_store.chromadb")
    @patch("rag_system.ingestion.vector_store.Chroma")
    def test_get_collection_stats(self, mock_chroma, mock_chromadb, settings, mock_embedding_function):
        """Test getting collection statistics."""
        # Mock ChromaDB client and collection
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 10
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_collection.return_value = mock_collection
        
        # Mock the LangChain Chroma wrapper
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance

        vector_store = VectorStore(settings, embedding_function=mock_embedding_function)
        stats = vector_store.get_collection_stats()

        assert stats["document_count"] == 10
        # Verify the actual ChromaDB client method was called
        mock_client.get_collection.assert_called_once_with(name=settings.collection_name)
        mock_collection.count.assert_called_once()

    def test_add_documents_mismatch(self, settings, mock_embedding_function, sample_documents):
        """Test adding documents with mismatched embeddings."""
        # Create fewer embeddings than documents
        mismatched_embeddings = [[0.1, 0.2, 0.3]]

        with pytest.raises(ValueError, match="Number of documents must match number of embeddings"):
            vector_store = VectorStore(settings, embedding_function=mock_embedding_function)
            vector_store.add_documents(sample_documents, mismatched_embeddings)


def test_generate_llm_response_mocked(settings_with_openai_key):
    """Test LLM response generation with mocked OpenAI."""
    with patch("langchain_openai.ChatOpenAI") as mock_chat_openai:
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = "Mocked response from OpenAI"
        mock_chat_openai.return_value = mock_llm

        rag_system = RAGSystem(settings=settings_with_openai_key)
        response = rag_system.generate_llm_response("Test prompt")

        assert response == "Mocked response from OpenAI"
        mock_llm.invoke.assert_called_once()


def test_generate_llm_response_raises_on_llm_failure(settings_with_openai_key):
    """Test that LLM failures are properly handled."""
    with patch("langchain_openai.ChatOpenAI") as mock_chat_openai:
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("OpenAI API error")
        mock_chat_openai.return_value = mock_llm

        rag_system = RAGSystem(settings=settings_with_openai_key)
        
        with pytest.raises(Exception, match="OpenAI API error"):
            rag_system.generate_llm_response("Test prompt")


def test_generate_llm_response_no_api_key(settings_without_openai_key):
    """Test that missing API key raises appropriate error."""
    rag_system = RAGSystem(settings=settings_without_openai_key)
    
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        rag_system.generate_llm_response("Test prompt")


def test_generate_rag_response_with_documents(monkeypatch):
    """Test RAG response generation with retrieved documents."""
    # Mock retrieval to return (Document, float) tuples
    mock_docs = [
        (Document(page_content="Relevant document 1", metadata={"source": "doc1.txt"}), 0.8),
        (Document(page_content="Relevant document 2", metadata={"source": "doc2.txt"}), 0.6)
    ]
    
    with patch("rag_system.rag_system.RAGSystem.query", return_value=mock_docs):
        with patch("rag_system.rag_system.RAGSystem.generate_llm_response", return_value="Generated response"):
            rag_system = RAGSystem(settings=Settings())
            response = rag_system.generate_rag_response("test query")
            assert "Generated response" in response


def test_generate_rag_response_filters_by_score(monkeypatch):
    """Test that RAG response filters documents by relevance score."""
    # One doc above threshold, one below
    mock_docs = [
        (Document(page_content="High relevance doc", metadata={"source": "doc1.txt"}), 0.8),
        (Document(page_content="Low relevance doc", metadata={"source": "doc2.txt"}), 0.3)
    ]
    
    with patch("rag_system.rag_system.RAGSystem.query", return_value=mock_docs):
        with patch("rag_system.rag_system.RAGSystem.generate_llm_response") as mock_llm:
            # Mock the LLM to return a response that includes the context
            def mock_llm_response(prompt):
                if "High relevance doc" in prompt:
                    return "Response based on high relevance document"
                return "Generic response"
            mock_llm.side_effect = mock_llm_response
            
            rag_system = RAGSystem(settings=Settings())
            response = rag_system.generate_rag_response("test query")
            
            # Verify the LLM was called with a prompt containing the high relevance doc
            mock_llm.assert_called_once()
            call_args = mock_llm.call_args[0][0]  # Get the prompt argument
            assert "High relevance doc" in call_args
            assert "Low relevance doc" not in call_args
            assert "Response based on high relevance document" in response


def test_generate_rag_response_all_below_threshold(monkeypatch):
    """Test RAG response when all documents are below relevance threshold."""
    # All docs below threshold
    mock_docs = [
        (Document(page_content="Low relevance doc 1", metadata={"source": "doc1.txt"}), 0.3),
        (Document(page_content="Low relevance doc 2", metadata={"source": "doc2.txt"}), 0.2)
    ]
    
    with patch("rag_system.rag_system.RAGSystem.query", return_value=mock_docs):
        with patch("rag_system.rag_system.RAGSystem.generate_llm_response") as mock_llm:
            # Mock the LLM to return a response for empty context
            def mock_llm_response(prompt):
                if "Context:" in prompt and "Low relevance doc" not in prompt:
                    return "I don't know based on the provided information."
                return "Generic response"
            mock_llm.side_effect = mock_llm_response
            
            rag_system = RAGSystem(settings=Settings())
            response = rag_system.generate_rag_response("test query")
            
            # Verify the LLM was called with an empty context
            mock_llm.assert_called_once()
            call_args = mock_llm.call_args[0][0]  # Get the prompt argument
            assert "Low relevance doc" not in call_args
            assert "I don't know based on the provided information." in response


def test_generate_rag_response_with_custom_prompt(monkeypatch):
    """Test RAG response with custom prompt template."""
    # Custom prompt template, all docs above threshold
    class CustomPromptBuilder(PromptBuilder):
        def __init__(self):
            super().__init__("Custom context: {context}\nQuestion: {question}\nAnswer:")
    
    mock_docs = [
        (Document(page_content="Relevant document", metadata={"source": "doc1.txt"}), 0.8)
    ]
    
    with patch("rag_system.rag_system.RAGSystem.query", return_value=mock_docs):
        with patch("rag_system.rag_system.RAGSystem.generate_llm_response") as mock_llm:
            # Mock the LLM to return a response that includes the custom prompt format
            def mock_llm_response(prompt):
                if "Custom context:" in prompt and "Relevant document" in prompt:
                    return "Custom response based on relevant document"
                return "Generic response"
            mock_llm.side_effect = mock_llm_response
            
            rag_system = RAGSystem(settings=Settings(), prompt_builder=CustomPromptBuilder())
            response = rag_system.generate_rag_response("test query")
            
            # Verify the LLM was called with the custom prompt format
            mock_llm.assert_called_once()
            call_args = mock_llm.call_args[0][0]  # Get the prompt argument
            assert "Custom context:" in call_args
            assert "Relevant document" in call_args
            assert "Custom response based on relevant document" in response
