"""
RAG System Demo

A demonstration script for the RAG system showing basic usage
of document ingestion and querying.
"""

from pathlib import Path

from rag_system.core.config import Settings
from rag_system.core.logging import setup_logging
from rag_system.rag_system import RAGSystem


def main() -> None:
    settings = Settings()
    setup_logging(log_level=settings.log_level, log_format=settings.log_format)
    print(f"[DEBUG] OPENAI_API_KEY from settings: {settings.openai_api_key}")

    print("🤖 RAG System Demo")
    print("=" * 50)

    # Initialize the system
    print("Initializing RAG system...")
    rag = RAGSystem(settings=settings)

    # Check if data directory exists
    data_dir = settings.data_directory
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

    print(f"📁 Found {len(supported_files)} supported files: ")
    for file in supported_files:
        print(f"   • {Path(file).name}")

    # Ingest documents
    print("\n📥 Ingesting documents...")
    try:
        stats = rag.ingest_documents()

        if stats.get("status") == "success":
            print("✅ Ingestion completed successfully!")
            print(
                f"   Original documents: {stats.get('original_documents', 0)}"
            )
            print(f"   Chunked documents: {stats.get('chunked_documents', 0)}")
            print(
                f"   Embeddings generated: "
                f"{stats.get('embeddings_generated', 0)}"
            )
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
            results = rag.query(query, k=2, include_scores=True)
            if results:
                for j, result in enumerate(results, 1):
                    if (
                        isinstance(result, tuple)
                        and len(result) == 2
                        and isinstance(result[1], (float, int))
                    ):
                        doc, score = result
                        print(f"Result {j}: ")
                        print(
                            f"  Source: "
                            f"{Path(doc.metadata.get('source', 'Unknown'))
                                .name}"
                        )
                        content_preview = doc.page_content[:150]
                        print(f"  Content: {content_preview} ...")
                        print(f"  Score: {score:.4f}")
                    else:
                        print(
                            f"Result {j}: ["
                            f"Skipped: Unexpected result format: "
                            f"{type(result)}]"
                        )
            else:
                print("  No results found above relevance threshold.")

            # Show the context and final LLM-augmented response
            print("\n[Enterprise] RAG-augmented LLM response:")
            # To log the context, we need to reconstruct it as in
            # generate_rag_response
            MIN_RELEVANCE_SCORE = (
                getattr(rag, "MIN_RELEVANCE_SCORE", 0.5)
                if hasattr(rag, "MIN_RELEVANCE_SCORE")
                else 0.5
            )
            filtered = []
            for result in results:
                if (
                    isinstance(result, tuple)
                    and len(result) == 2
                    and isinstance(result[1], (float, int))
                ):
                    doc, score = result
                    if score >= MIN_RELEVANCE_SCORE:
                        filtered.append(doc)
            if not filtered:
                context = ""
            else:
                context_chunks = []
                for doc in filtered:
                    if hasattr(doc, "page_content"):
                        context_chunks.append(str(doc.page_content))
                    elif isinstance(doc, dict):
                        context_chunks.append(
                            str(doc.get("page_content", str(doc)))
                        )
                    else:
                        context_chunks.append(str(doc))
                context = "\n---\n".join(context_chunks)
            print("[Enterprise] Context passed to LLM:")
            print(context if context else "[EMPTY CONTEXT]")
            llm_response = rag.generate_rag_response(query, k=2)
            print("[Enterprise] LLM Response:")
            print(llm_response)
        except Exception as e:
            print(f"  ❌ Query failed: {e}")

    # System statistics
    print("\n📊 System Statistics:")
    print("-" * 40)
    try:
        stats = rag.get_system_stats()

        vector_stats = stats.get("vector_store", {})
        print(
            f"Documents in database: {vector_stats.get('document_count', 0)}"
        )
        print(
            f"Collection name: "
            f"{vector_stats.get('collection_name', 'Unknown')}"
        )
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
