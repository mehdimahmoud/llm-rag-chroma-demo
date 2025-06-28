"""
Text chunker implementation for breaking text into smaller pieces.
"""
from typing import List, Optional
import re

from ..core.interfaces import TextChunker
from ..models.document import DocumentChunk, IngestionConfig
from ...logging.logger import IngestionLogger


class ParagraphTextChunker(TextChunker):
    """Paragraph-based text chunker."""
    
    def __init__(self, logger: Optional[IngestionLogger] = None):
        """
        Initialize the text chunker.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or IngestionLogger()
    
    def chunk_text(self, text: str, config: IngestionConfig, source_file: str) -> List[DocumentChunk]:
        """
        Chunk text into smaller pieces based on paragraphs.
        
        Args:
            text: Text to chunk
            config: Ingestion configuration
            source_file: Source filename for the chunks
            
        Returns:
            List of text chunks
        """
        try:
            self.logger.debug(f"Chunking text from {source_file} (min length: {config.chunk_min_length})")
            
            # Split text into paragraphs
            paragraphs = self._split_into_paragraphs(text)
            
            # Filter out paragraphs that are too short
            valid_paragraphs = [
                p.strip() for p in paragraphs 
                if len(p.strip()) >= config.chunk_min_length
            ]
            
            # Create document chunks
            chunks = []
            for i, paragraph in enumerate(valid_paragraphs):
                chunk_id = f"{source_file}_chunk_{i}"
                chunk = DocumentChunk(
                    id=chunk_id,
                    text=paragraph,
                    source_file=source_file,
                    chunk_index=i,
                    metadata={"source": source_file, "chunk_index": i}
                )
                chunks.append(chunk)
            
            self.logger.debug(f"Created {len(chunks)} chunks from {source_file}")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error chunking text from {source_file}: {e}")
            raise
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.
        
        Args:
            text: Text to split
            
        Returns:
            List of paragraphs
        """
        # Split by newlines and filter out empty lines
        paragraphs = re.split(r'\n+', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def chunk_text_with_custom_strategy(self, text: str, strategy: str, **kwargs) -> List[DocumentChunk]:
        """
        Chunk text using a custom strategy.
        
        Args:
            text: Text to chunk
            strategy: Chunking strategy ('paragraph', 'sentence', 'fixed_size')
            **kwargs: Strategy-specific parameters
            
        Returns:
            List of text chunks
        """
        if strategy == 'paragraph':
            return self._chunk_by_paragraphs(text, **kwargs)
        elif strategy == 'sentence':
            return self._chunk_by_sentences(text, **kwargs)
        elif strategy == 'fixed_size':
            return self._chunk_by_fixed_size(text, **kwargs)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    def _chunk_by_paragraphs(self, text: str, **kwargs) -> List[DocumentChunk]:
        """Chunk text by paragraphs."""
        paragraphs = self._split_into_paragraphs(text)
        chunks = []
        for i, paragraph in enumerate(paragraphs):
            chunk = DocumentChunk(
                id=f"chunk_{i}",
                text=paragraph,
                source_file="unknown",
                chunk_index=i,
                metadata={"chunk_index": i, "strategy": "paragraph"}
            )
            chunks.append(chunk)
        return chunks
    
    def _chunk_by_sentences(self, text: str, **kwargs) -> List[DocumentChunk]:
        """Chunk text by sentences."""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                chunk = DocumentChunk(
                    id=f"chunk_{i}",
                    text=sentence,
                    source_file="unknown",
                    chunk_index=i,
                    metadata={"chunk_index": i, "strategy": "sentence"}
                )
                chunks.append(chunk)
        return chunks
    
    def _chunk_by_fixed_size(self, text: str, **kwargs) -> List[DocumentChunk]:
        """Chunk text by fixed size."""
        chunk_size = kwargs.get('chunk_size', 1000)
        overlap = kwargs.get('overlap', 100)
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            chunk = DocumentChunk(
                id=f"chunk_{chunk_index}",
                text=chunk_text,
                source_file="unknown",
                chunk_index=chunk_index,
                metadata={"chunk_index": chunk_index, "strategy": "fixed_size", "start": start, "end": end}
            )
            chunks.append(chunk)
            
            start = end - overlap
            chunk_index += 1
        
        return chunks 