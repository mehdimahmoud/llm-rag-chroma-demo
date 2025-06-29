import re
import structlog

from typing import List

from ..core.interfaces import TextChunker
from ..models.document import DocumentChunk, IngestionConfig

"""
Text chunker implementation for breaking text into smaller pieces.
"""


class ParagraphTextChunker(TextChunker):
    """Paragraph-based text chunker."""

    def __init__(self, _logger=None):
        """
        Initialize the text chunker.

        Args:
            logger: Logger instance (structlog logger)
        """
        self.logger = structlog.get_logger("text_chunker")

    def chunk_text(
        self, text: str, config: IngestionConfig, source_file: str
    ) -> List[DocumentChunk]:
        """
        Chunk text into smaller pieces based on paragraphs.

        Args:
            text: Text to chunk
            config: Ingestion configuration
            source_file: Source filename for the chunks

        Returns:
            List of text chunks
        """
        self.logger.debug(
            "Starting text chunking",
            source_file=source_file,
            text_length=len(text),
            chunk_min_length=config.chunk_min_length,
        )

        if not text.strip():
            self.logger.warning(
                "Empty text provided for chunking", source_file=source_file
            )
            return []

        # Split text into paragraphs
        paragraphs = re.split(r"\n\s*\n", text.strip())
        self.logger.debug(
            "Split text into paragraphs",
            source_file=source_file,
            paragraph_count=len(paragraphs),
        )

        chunks = []
        chunk_id = 0

        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Check if paragraph meets minimum length requirement
            if len(paragraph) < config.chunk_min_length:
                self.logger.debug(
                    "Paragraph too short, skipping",
                    source_file=source_file,
                    paragraph_index=i,
                    paragraph_length=len(paragraph),
                )
                continue

            # Create chunk
            chunk = DocumentChunk(
                id=str(chunk_id),
                text=paragraph,
                source_file=source_file,
                chunk_index=i,
                metadata={
                    "source": source_file,
                    "chunk_index": i,
                    "strategy": "paragraph",
                },
            )
            chunks.append(chunk)
            chunk_id += 1

            self.logger.debug(
                "Created chunk",
                source_file=source_file,
                chunk_id=chunk_id,
                chunk_length=len(paragraph),
            )

        self.logger.info(
            "Text chunking completed",
            source_file=source_file,
            total_chunks=len(chunks),
            original_paragraphs=len(paragraphs),
        )

        return chunks

    def chunk_text_with_custom_strategy(
        self, text: str, strategy: str, **kwargs
    ) -> List[DocumentChunk]:
        """
        Chunk text using a custom strategy.

        Args:
            text: Text to chunk
            strategy: Chunking strategy ('paragraph', 'sentence', 'fixed_size')
            **kwargs: Strategy-specific parameters

        Returns:
            List of text chunks
        """
        if strategy == "paragraph":
            return self._chunk_by_paragraphs(text, **kwargs)
        elif strategy == "sentence":
            return self._chunk_by_sentences(text, **kwargs)
        elif strategy == "fixed_size":
            return self._chunk_by_fixed_size(text, **kwargs)
        else:
            raise ValueError("Unknown chunking strategy: {strategy}")

    def _chunk_by_paragraphs(self, text: str, **kwargs) -> List[DocumentChunk]:
        """Chunk text by paragraphs."""
        paragraphs = self._split_into_paragraphs(text)
        chunks = []
        for i, paragraph in enumerate(paragraphs):
            chunk = DocumentChunk(
                id="chunk_{i}",
                text=paragraph,
                source_file="unknown",
                chunk_index=i,
                metadata={"chunk_index": i, "strategy": "paragraph"},
            )
            chunks.append(chunk)
        return chunks

    def _chunk_by_sentences(self, text: str, **kwargs) -> List[DocumentChunk]:
        """Chunk text by sentences."""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r"[.!?]+", text)
        chunks = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                chunk = DocumentChunk(
                    id="chunk_{i}",
                    text=sentence,
                    source_file="unknown",
                    chunk_index=i,
                    metadata={"chunk_index": i, "strategy": "sentence"},
                )
                chunks.append(chunk)
        return chunks

    def _chunk_by_fixed_size(self, text: str, **kwargs) -> List[DocumentChunk]:
        """Chunk text by fixed size."""
        chunk_size = kwargs.get("chunk_size", 1000)
        overlap = kwargs.get("overlap", 100)

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunk = DocumentChunk(
                id="chunk_{chunk_index}",
                text=chunk_text,
                source_file="unknown",
                chunk_index=chunk_index,
                metadata={
                    "chunk_index": chunk_index,
                    "strategy": "fixed_size",
                    "start": start,
                    "end": end,
                },
            )
            chunks.append(chunk)

            start = end - overlap
            chunk_index += 1

        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text: Text to split

        Returns:
            List of paragraphs
        """
        # Split by newlines and filter out empty lines
        paragraphs = re.split(r"\n+", text)
        return [p.strip() for p in paragraphs if p.strip()]
