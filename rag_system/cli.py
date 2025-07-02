"""
Command-line interface for the RAG system.

This module provides a user-friendly CLI for interacting with the RAG system,
including document ingestion, querying, and system management.
"""

import argparse
import sys
from pathlib import Path

from .core.config import Settings
from .core.logging import get_logger, setup_logging
from .rag_system import RAGSystem

# from typing import List, Optional


logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="RAG system using LangChain and ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all documents in the data directory
  rag-demo ingest

  # Ingest specific files
  rag-demo ingest --files data/document1.pdf data/document2.txt

  # Query the system
  rag-demo query "What are the HR policies?"

  # Get system statistics
  rag-demo stats

  # Clear the database
  rag-demo clear
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest documents into the system"
    )
    ingest_parser.add_argument(
        "--files",
        nargs="+",
        help=(
            "Specific files to ingest "
            "(default: all supported files in data directory)"
        ),
    )
    ingest_parser.add_argument(
        "--data-dir", type=Path, help="Data directory (default: from settings)"
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument("query", help="Search query")
    query_parser.add_argument(
        "-k",
        "--num-results",
        type=int,
        default=4,
        help="Number of results to return (default: 4)",
    )
    query_parser.add_argument(
        "--include-scores",
        action="store_true",
        help="Include similarity scores in results",
    )

    # Stats command
    subparsers.add_parser("stats", help="Show system statistics")

    # Clear command
    subparsers.add_parser("clear", help="Clear the vector database")

    # Interactive command
    subparsers.add_parser("interactive", help="Start interactive mode")

    # Global options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-format",
        choices=["json", "text"],
        default="text",
        help="Log format (default: text)",
    )

    return parser


def handle_ingest(args: argparse.Namespace, rag_system: RAGSystem) -> None:
    """Handle the ingest command."""
    logger.info("Starting document ingestion")

    try:
        if args.files:
            # Convert string paths to Path objects
            file_paths = [Path(f) for f in args.files]
            stats = rag_system.ingest_documents([str(f) for f in file_paths])
        else:
            stats = rag_system.ingest_documents()

        print("\n✅ Ingestion completed successfully!")
        print(f"   Original documents: {stats.get('original_documents', 0)}")
        print(f"   Chunked documents: {stats.get('chunked_documents', 0)}")
        print(
            f"   Embeddings generated: {stats.get('embeddings_generated', 0)}"
        )
        print(f"   Chunked documents: {stats.get('chunked_documents', 0)}")
        print(f"   Documents stored: {stats.get('documents_stored', 0)}")

    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        print(f"❌ Ingestion failed: {e}")
        sys.exit(1)


def handle_query(args: argparse.Namespace, rag_system: RAGSystem) -> None:
    """Handle the query command."""
    logger.info("Processing query", query=args.query)

    try:
        results = rag_system.query(
            query=args.query,
            k=args.num_results,
            include_scores=args.include_scores,
        )

        print(f"\n🔍 Query: {args.query}")
        print(f"📊 Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            if args.include_scores:
                doc, score = result
                print(f"{i}. [Score: {score:.4f}]")
            else:
                doc = result
                print(f"{i}.")

            print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"   Content: {doc.page_content[:200]}...")
            print()

    except Exception as e:
        logger.error("Query failed", error=str(e))
        print(f"❌ Query failed: {e}")
        sys.exit(1)


def handle_stats(args: argparse.Namespace, rag_system: RAGSystem) -> None:
    """Handle the stats command."""
    logger.info("Retrieving system statistics")

    try:
        stats = rag_system.get_system_stats()

        print("\n📈 System Statistics:")
        print("=" * 50)

        # Vector store stats
        vector_stats = stats.get("vector_store", {})
        print(
            f"📚 Collection: {vector_stats.get('collection_name', 'Unknown')}"
        )
        print(f"📄 Documents in DB: {vector_stats.get('document_count', 0)}")

        # File type summary
        file_types = stats.get("file_types", {})
        if file_types:
            print("\n📁 Files in data directory:")
            for file_type, count in file_types.items():
                print(f"   {file_type}: {count}")

        # Document sources
        sources = stats.get("document_sources", [])
        print(f"\n🗂️  Document sources in DB: {len(sources)}")
        for source in sources:
            print(f"   • {Path(source).name}")

    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
        print(f"❌ Failed to get statistics: {e}")
        sys.exit(1)


def handle_clear(
    args: argparse.Namespace,
    rag_system: RAGSystem,
) -> None:
    """Handle the clear command."""
    logger.info("Clearing vector database")

    try:
        rag_system.clear_database()
        print("✅ Vector database cleared successfully")

    except Exception as e:
        logger.error("Failed to clear database", error=str(e))
        print(f"❌ Failed to clear database: {e}")
        sys.exit(1)


def handle_interactive(
    args: argparse.Namespace,
    rag_system: RAGSystem,
) -> None:
    """Handle the interactive command."""
    logger.info("Starting interactive mode")

    print("\n🤖 RAG System Interactive Mode")
    print("=" * 40)
    print("Commands:")
    print("  query <text>     - Search the knowledge base")
    print("  ingest           - Ingest all documents")
    print("  stats            - Show system statistics")
    print("  clear            - Clear the database")
    print("  quit/exit        - Exit interactive mode")
    print()

    while True:
        try:
            command = input("rag> ").strip()

            if not command:
                continue

            parts = command.split(" ", 1)
            cmd = parts[0].lower()
            args_text = parts[1] if len(parts) > 1 else ""

            if cmd in ["quit", "exit"]:
                print("👋 Goodbye!")
                break
            elif cmd == "query":
                if not args_text:
                    print("❌ Please provide a query")
                    continue

                # Create a mock args object for the query handler
                mock_args = argparse.Namespace(
                    query=args_text, num_results=4, include_scores=False
                )
                handle_query(mock_args, rag_system)

            elif cmd == "ingest":
                mock_args = argparse.Namespace(files=None, data_dir=None)
                handle_ingest(mock_args, rag_system)

            elif cmd == "stats":
                mock_args = argparse.Namespace()
                handle_stats(mock_args, rag_system)

            elif cmd == "clear":
                mock_args = argparse.Namespace()
                handle_clear(mock_args, rag_system)

            else:
                print(f"❌ Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Instantiate settings and setup logging
    settings = Settings()
    setup_logging(log_level=settings.log_level, log_format=settings.log_format)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize RAG system with settings
        rag_system = RAGSystem(settings=settings)

        # Handle commands
        if args.command == "ingest":
            handle_ingest(args, rag_system)
        elif args.command == "query":
            handle_query(args, rag_system)
        elif args.command == "stats":
            handle_stats(args, rag_system)
        elif args.command == "clear":
            handle_clear(args, rag_system)
        elif args.command == "interactive":
            handle_interactive(args, rag_system)
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)

    except Exception as e:
        logger.error("CLI execution failed", error=str(e))
        print(f"❌ System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
