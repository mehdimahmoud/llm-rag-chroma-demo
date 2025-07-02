"""
Text processing and chunking functionality.

This module handles text chunking, embedding generation, and text preprocessing
for optimal RAG performance.
"""

from typing import List, Optional

# import langchain_community.embeddings
import torch
from langchain_core.documents import Document
# from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.logging import get_logger

# from sentence_transformers import SentenceTransformer


logger = get_logger(__name__)


class TextProcessor:
    """Handles text processing, chunking, and embedding generation."""

    def __init__(
        self,
        settings,
        embedding_model_name: Optional[str] = None,
        chunk_size: Optional[int] = None,  # legacy, not used in adaptive mode
        chunk_overlap: Optional[int] = None,  # legacy, not used in adaptive mode
    ):
        """
        Initialize the text processor.

        Args:
            settings: Settings instance
            embedding_model_name: Name of the sentence transformer model
        """
        self.settings = settings
        self.embedding_model_name = (
            embedding_model_name or settings.embedding_model_name
        )
        self.small_chunk_size = settings.small_chunk_size
        self.small_chunk_overlap = settings.small_chunk_overlap
        self.large_chunk_size = settings.large_chunk_size
        self.large_chunk_overlap = settings.large_chunk_overlap
        self.size_threshold = settings.chunk_size_threshold

        # Initialize embedding model
        self._embedding_model = None

        logger.info(
            "Text processor initialized",
            embedding_model=self.embedding_model_name,
            small_chunk_size=self.small_chunk_size,
            small_chunk_overlap=self.small_chunk_overlap,
            large_chunk_size=self.large_chunk_size,
            large_chunk_overlap=self.large_chunk_overlap,
            size_threshold=self.size_threshold,
        )

    # @property
    # def embedding_model(self) -> SentenceTransformer:
    #     """Get or initialize the embedding model."""
    #     if self._embedding_model is None:
    #         logger.info(
    #         "Loading embedding model",
    #         model_name=self.embedding_model_name,
    #     )
    #         self._embedding_model = (
    #             SentenceTransformer(self.embedding_model_name)
    #         )
    #         logger.info("Embedding model loaded successfully")
    #     return self._embedding_model

    @property
    def embedding_model(self):
        return HuggingFaceEmbeddings(
            model_name=f"sentence-transformers/{self.embedding_model_name}",
            model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for processing, using adaptive chunking.
        """
        if not documents:
            logger.warning("No documents provided for chunking")
            return []

        logger.info(
            "Starting document chunking",
            document_count=len(documents),
        )

        chunked_documents = []
        for doc in documents:
            if len(doc.page_content) < self.size_threshold:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.small_chunk_size,
                    chunk_overlap=self.small_chunk_overlap,
                    length_function=len,
                    separators=["\n\n", "\n", " ", ""],
                )
            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.large_chunk_size,
                    chunk_overlap=self.large_chunk_overlap,
                    length_function=len,
                    separators=["\n\n", "\n", " ", ""],
                )
            chunks = splitter.split_documents([doc])
            chunked_documents.extend(chunks)

        logger.info(
            "Document chunking completed",
            original_documents=len(documents),
            total_chunks=len(chunked_documents),
        )

        return chunked_documents

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("No texts provided for embedding")
            return []

        logger.info("Generating embeddings", text_count=len(texts))

        try:
            embeddings = self.embedding_model.embed_documents(texts)
            embeddings_list = (
                embeddings if isinstance(embeddings, list) else embeddings.tolist()
            )

            logger.info(
                "Embeddings generated successfully",
                text_count=len(texts),
                embedding_dimension=(len(embeddings_list[0]) if embeddings_list else 0),
            )

            return embeddings_list

        except Exception as e:
            logger.error("Failed to generate embeddings", error=str(e))
            raise

    def process_documents(
        self, documents: List[Document]
    ) -> tuple[List[Document], List[List[float]]]:
        """
        Process documents: chunk and generate embeddings.

        Args:
            documents: List of documents to process

        Returns:
            Tuple of (chunked_documents, embeddings)
        """
        logger.info("Starting document processing", document_count=len(documents))

        # Chunk documents
        chunked_docs = self.chunk_documents(documents)

        # Extract text content
        texts = [doc.page_content for doc in chunked_docs]

        # Generate embeddings
        embeddings = self.generate_embeddings(texts)

        logger.info(
            "Document processing completed",
            original_documents=len(documents),
            chunked_documents=len(chunked_docs),
            embeddings_generated=len(embeddings),
        )

        return chunked_docs, embeddings
