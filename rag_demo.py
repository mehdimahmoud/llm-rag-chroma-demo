"""
RAG System Demo

A demonstration script for the RAG system showing basic usage
of document ingestion and querying.
"""

import os
from pathlib import Path

from rag_system.rag_system import RAGSystem
from rag_system.core.logging import setup_logging

# Setup logging
setup_logging(log_level="INFO", log_format="text")


def main():
    """Run the RAG system demo."""
    print("🤖 RAG System Demo")
    print("=" * 50)
    
    # Initialize the system
    print("Initializing RAG system...")
    rag = RAGSystem()
    
    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Data directory '{data_dir}' not found!")
        print("Please create the data directory and add some documents.")
        return
    
    # Get supported files
    supported_files = rag.get_supported_files()
    if not supported_files:
        print("❌ No supported files found in data directory!")
        print("Supported formats: PDF, TXT, DOCX, MD, CSV, XLSX")
        return
    
    print(f"📁 Found {len(supported_files)} supported files:")
    for file in supported_files:
        print(f"   • {Path(file).name}")
    
    # Ingest documents
    print("\n📥 Ingesting documents...")
    try:
        stats = rag.ingest_documents()
        
        if stats.get("status") == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Original documents: {stats.get('original_documents', 0)}")
            print(f"   Chunked documents: {stats.get('chunked_documents', 0)}")
            print(f"   Embeddings generated: {stats.get('embeddings_generated', 0)}")
            print(f"   Documents stored: {stats.get('documents_stored', 0)}")
        else:
            print("⚠️  No documents were processed")
            return
            
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return
    
    # Demo queries
    demo_queries = [
        "What are the HR policies?",
        "What is the vacation policy?",
        "What are the benefits?",
        "What is the dress code?",
    ]
    
    print("\n🔍 Running demo queries...")
    for i, query in enumerate(demo_queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 40)
        
        try:
            results = rag.query(query, k=2)
            
            if results:
                for j, (doc, score) in enumerate(results, 1):
                    print(f"Result {j}:")
                    print(f"  Source: {Path(doc.metadata.get('source', 'Unknown')).name}")
                    print(f"  Content: {doc.page_content[:150]}...")
                    print(f"  Score: {score:.4f}")  # Optional: Print the score if needed
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ❌ Query failed: {e}")
    
    # System statistics
    print("\n📊 System Statistics:")
    print("-" * 40)
    try:
        stats = rag.get_system_stats()
        
        vector_stats = stats.get("vector_store", {})
        print(f"Documents in database: {vector_stats.get('document_count', 0)}")
        print(f"Collection name: {vector_stats.get('collection_name', 'Unknown')}")
        print(f"Total sources: {stats.get('total_sources', 0)}")
        
    except Exception as e:
        print(f"❌ Failed to get statistics: {e}")
    
    print("\n✅ Demo completed successfully!")
    print("\nNext steps:")
    print("  • Run 'make run-ui' to start the web interface")
    print("  • Run 'rag-demo interactive' for interactive mode")
    print("  • Check the documentation for more features")


if __name__ == "__main__":
    main() 