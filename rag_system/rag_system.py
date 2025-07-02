"""
Main RAG system orchestrator.

This module provides the main interface for the RAG system, coordinating
document ingestion, processing, and querying operations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from langchain_core.documents import Document

from .core.logging import get_logger
from .ingestion.document_loader import DocumentLoader
from .ingestion.text_processor import TextProcessor
from .ingestion.vector_store import VectorStore

logger = get_logger(__name__)


class PromptBuilder:
    """
    Enterprise-grade, configurable prompt builder for RAG.
    """
    def __init__(self, template: str | None = None):
        self.template = template or (
            "You are an expert assistant. Use the following context to answer the user's question.\n"
            "If the answer is not in the context, say 'I don't know based on the provided information.'\n\n"
            "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
        )

    def build(self, context: str, question: str) -> str:
        return self.template.format(context=context, question=question)


class RAGSystem:
    """Main RAG system orchestrator."""

    def __init__(self, settings, prompt_builder: PromptBuilder | None = None):
        """Initialize the RAG system with all components."""
        self.settings = settings
        self.MIN_RELEVANCE_SCORE = getattr(settings, "min_relevance_score", 0.5)
        logger.info("Initializing RAG system")

        # Initialize components with settings
        self.document_loader = DocumentLoader(settings)
        self.text_processor = TextProcessor(settings)

        # Create embedding function for vector store
        embedding_function = self.text_processor.embedding_model
        print(
            "Has embed_documents: " f"{hasattr(embedding_function, 'embed_documents')}",
        )

        self.vector_store = VectorStore(settings, embedding_function=embedding_function)

        self.prompt_builder = prompt_builder or PromptBuilder()

        logger.info("RAG system initialized successfully")

    def ingest_documents(
        self, file_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ingest documents into the RAG system.

        Args:
            file_paths: Optional list of specific file paths to process

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info("Starting document ingestion")

        try:
            # Load documents
            if file_paths:
                # Load specific files
                documents = []
                for file_path in file_paths:
                    doc = self.document_loader.load_document(Path(file_path))
                    documents.extend(doc)
            else:
                # Load all documents
                documents = self.document_loader.load_all_documents()

            if not documents:
                logger.warning("No documents found for ingestion")
                return {"status": "no_documents", "documents_processed": 0}

            # Process documents (chunk and embed)
            chunked_docs, embeddings = self.text_processor.process_documents(
                documents,
            )

            # Store in vector database
            doc_ids = self.vector_store.add_documents(chunked_docs, embeddings)

            stats = {
                "status": "success",
                "original_documents": len(documents),
                "chunked_documents": len(chunked_docs),
                "embeddings_generated": len(embeddings),
                "documents_stored": len(doc_ids),
            }

            logger.info("Document ingestion completed", stats=stats)
            return stats

        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            raise

    def query(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        include_scores: bool = False,
    ) -> List[Document] | List[tuple[Document, float]]:
        """
        Query the RAG system.

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            include_scores: Whether to include similarity scores

        Returns:
            List of documents or (document, score) tuples
        """
        logger.info("Processing query", query=query, k=k)

        try:
            if include_scores:
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter,
                )
            else:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter,
                )

            logger.info("Query completed", results_count=len(results))
            return results

        except Exception as e:
            logger.error("Query failed", query=query, error=str(e))
            raise

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.

        Returns:
            Dictionary with system statistics
        """
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats()

            # Get file type summary
            file_summary = self.document_loader.get_file_type_summary()

            # Get document sources
            sources = self.vector_store.get_document_sources()

            stats = {
                "vector_store": vector_stats,
                "file_types": file_summary,
                "document_sources": sources,
                "total_sources": len(sources),
            }

            logger.info("System statistics retrieved", stats=stats)
            return stats

        except Exception as e:
            logger.error("Failed to get system statistics", error=str(e))
            raise

    def clear_database(self) -> None:
        """Clear all data from the vector database."""
        logger.info("Clearing vector database")

        try:
            self.vector_store.delete_collection()
            logger.info("Vector database cleared successfully")
            # Re-instantiate VectorStore to ensure a new collection is created and referenced
            self.vector_store = VectorStore(
                embedding_function=self.text_processor.embedding_model
            )
        except Exception as e:
            logger.error("Failed to clear vector database", error=str(e))
            raise

    def get_document_sources(self) -> List[str]:
        """
        Get list of document sources in the database.

        Returns:
            List of source file paths
        """
        return self.vector_store.get_document_sources()

    def get_supported_files(self) -> List[str]:
        """
        Get list of supported files in the data directory.

        Returns:
            List of file paths
        """
        files = self.document_loader.get_supported_files()
        return [str(f) for f in files]

    def _get_llm(self):
        """
        Initialize and return a ChatOpenAI instance using settings only.
        """
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key is required to use OpenAI LLM features. Please set openai_api_key in your config or environment.")
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr
        api_key = self.settings.openai_api_key
        if not isinstance(api_key, SecretStr):
            api_key = SecretStr(api_key)
        return ChatOpenAI(
            model=self.settings.openai_model_name,
            api_key=api_key,
        )

    def generate_llm_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM given a prompt.

        Args:
            prompt: The input prompt string

        Returns:
            The LLM's response as a string
        """
        llm = self._get_llm()
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

    def generate_rag_response(self, query: str, k: int = 4) -> str:
        """
        Retrieve top-k relevant documents (with scores), filter by relevance, build a prompt, and generate an answer using the LLM.

        Args:
            query: The user query
            k: Number of top documents to retrieve

        Returns:
            The LLM's answer as a string
        """
        # Retrieve top-k relevant documents with scores
        results = self.query(query, k=k, include_scores=True)
        filtered = []
        for result in results:
            # Only process (Document, float) tuples
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], (float, int)):
                doc, score = result
                doc_preview_val = getattr(doc, "page_content", doc)
                doc_preview = str(doc_preview_val)[:100]
                logger.info("Retrieved document with score", score=score, doc_preview=doc_preview)
                if score >= self.MIN_RELEVANCE_SCORE:
                    filtered.append(doc)
                else:
                    logger.info("Filtered out document below threshold", score=score, threshold=self.MIN_RELEVANCE_SCORE)
            else:
                logger.warning("Skipping result with unexpected format", result_type=str(type(result)), result=str(result))
        if not filtered:
            context = ""
        else:
            context_chunks = []
            for doc in filtered:
                if hasattr(doc, "page_content"):
                    context_chunks.append(str(doc.page_content))
                elif isinstance(doc, dict):
                    context_chunks.append(str(doc.get("page_content", str(doc))))
                else:
                    context_chunks.append(str(doc))
            context = "\n---\n".join(context_chunks)
        prompt = self.prompt_builder.build(context=context, question=query)
        return self.generate_llm_response(prompt)
