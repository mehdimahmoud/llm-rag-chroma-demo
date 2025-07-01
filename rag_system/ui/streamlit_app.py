"""
Streamlit web application for the RAG system.

This module provides a modern web interface for interacting
with the RAG system,
including document ingestion, querying, and system monitoring.
"""

from pathlib import Path

import streamlit as st

from ..core.config import settings
from ..core.logging import get_logger, setup_logging
from ..rag_system import RAGSystem

# from typing import List, Optional


# Setup logging
setup_logging(log_level="INFO", log_format="text")
logger = get_logger(__name__)


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="RAG System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🤖 RAG System")
    st.markdown("Retrieval-Augmented Generation with LangChain and ChromaDB")

    # Initialize session state
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
        st.session_state.initialized = False

    # Sidebar
    with st.sidebar:
        st.header("System Control")

        if st.button("🔄 Initialize System"):
            with st.spinner("Initializing RAG system..."):
                try:
                    st.session_state.rag_system = RAGSystem()
                    st.session_state.initialized = True
                    st.success("System initialized successfully!")
                except Exception as e:
                    st.error(f"Failed to initialize system: {e}")
                    logger.error("System initialization failed", error=str(e))

        if st.session_state.initialized:
            st.success("✅ System Ready")

            if st.button("🗑️ Clear Database"):
                if st.session_state.rag_system:
                    with st.spinner("Clearing database..."):
                        try:
                            st.session_state.rag_system.clear_database()
                            st.success("Database cleared successfully!")
                        except Exception as e:
                            st.error(f"Failed to clear database: {e}")

        # System info
        st.header("System Info")
        st.info(f"Data Directory: {settings.data_directory}")
        st.info(f"Collection: {settings.collection_name}")
        st.info(f"Embedding Model: {settings.embedding_model_name}")

    # Main content
    if not st.session_state.initialized:
        st.warning("Please initialize the system from the sidebar first.")
        return

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📚 Ingest", "🔍 Query", "📊 Statistics", "⚙️ Settings"]
    )

    with tab1:
        render_ingest_tab()

    with tab2:
        render_query_tab()

    with tab3:
        render_stats_tab()

    with tab4:
        render_settings_tab()


def render_ingest_tab() -> None:
    """Render the document ingestion tab."""
    st.header("📚 Document Ingestion")

    if not st.session_state.rag_system:
        st.error("System not initialized")
        return

    # File upload
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "txt", "docx", "md", "csv", "xlsx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} files:")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.type})")

    # Ingest options
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Ingest All Documents"):
            with st.spinner("Ingesting documents..."):
                try:
                    stats = st.session_state.rag_system.ingest_documents()

                    if stats.get("status") == "success":
                        st.success("✅ Ingestion completed successfully!")

                        # Display statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                "Original Docs",
                                stats.get("original_documents", 0),
                            )
                        with col2:
                            st.metric(
                                "Chunked Docs",
                                stats.get("chunked_documents", 0),
                            )
                        with col3:
                            st.metric(
                                "Embeddings",
                                stats.get("embeddings_generated", 0),
                            )
                        with col4:
                            st.metric(
                                "Stored",
                                stats.get("documents_stored", 0),
                            )
                    else:
                        st.warning("No documents found for ingestion")

                except Exception as e:
                    st.error(f"❌ Ingestion failed: {e}")
                    logger.error("Ingestion failed", error=str(e))

    with col2:
        if st.button("📋 Show Supported Files"):
            try:
                files = st.session_state.rag_system.get_supported_files()
                if files:
                    st.write("**Supported files in data directory:**")
                    for file in files:
                        st.write(f"- {Path(file).name}")
                else:
                    st.info("No supported files found in data directory")
            except Exception as e:
                st.error(f"Failed to get files: {e}")


def render_query_tab() -> None:
    """Render the query tab."""
    st.header("🔍 Query System")

    if not st.session_state.rag_system:
        st.error("System not initialized")
        return

    # Query input
    query = st.text_input(
        "Enter your query:",
        placeholder="What are the HR policies?",
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        num_results = st.slider(
            "Number of results:",
            min_value=1,
            max_value=10,
            value=4,
        )

    with col2:
        include_scores = st.checkbox("Include scores")

    if st.button("🔍 Search") and query:
        with st.spinner("Searching..."):
            try:
                results = st.session_state.rag_system.query(
                    query=query, k=num_results, include_scores=include_scores
                )

                if results:
                    st.success(f"Found {len(results)} results")

                    for i, result in enumerate(results, 1):
                        with st.expander(f"Result {i}"):
                            if include_scores:
                                doc, score = result
                                st.write(f"**Score:** {score:.4f}")
                            else:
                                doc = result

                            st.write(
                                f"**Source:** "
                                f"{
                                    Path(
                                        doc.metadata.get("source", "Unknown")
                                    ).name
                                }"
                            )
                            st.write("**Content:**")
                            st.text(doc.page_content)
                else:
                    st.info("No results found")

            except Exception as e:
                st.error(f"❌ Query failed: {e}")
                logger.error("Query failed", error=str(e))


def render_stats_tab() -> None:
    """Render the statistics tab."""
    st.header("📊 System Statistics")

    if not st.session_state.rag_system:
        st.error("System not initialized")
        return

    if st.button("🔄 Refresh Statistics"):
        with st.spinner("Loading statistics..."):
            try:
                stats = st.session_state.rag_system.get_system_stats()

                # Vector store stats
                vector_stats = stats.get("vector_store", {})
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Documents in DB",
                        vector_stats.get("document_count", 0),
                    )

                with col2:
                    st.metric(
                        "Collection",
                        vector_stats.get("collection_name", "Unknown"),
                    )

                with col3:
                    st.metric("Total Sources", stats.get("total_sources", 0))

                # File types
                file_types = stats.get("file_types", {})
                if file_types:
                    st.subheader("📁 Files by Type")
                    for file_type, count in file_types.items():
                        st.write(f"- {file_type}: {count}")

                # Document sources
                sources = stats.get("document_sources", [])
                if sources:
                    st.subheader("🗂️ Document Sources")
                    for source in sources:
                        st.write(f"- {Path(source).name}")

            except Exception as e:
                st.error(f"❌ Failed to load statistics: {e}")
                logger.error("Failed to load statistics", error=str(e))


def render_settings_tab() -> None:
    """Render the settings tab."""
    st.header("⚙️ System Settings")

    st.subheader("Current Configuration")

    # Display current settings
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Data Settings:**")
        st.write(f"- Data Directory: {settings.data_directory}")
        st.write(
            f"- Supported Types: {', '.join(settings.supported_file_types)}",
        )

        st.write("**Vector Store Settings:**")
        st.write(f"- Persist Directory: {settings.chroma_persist_directory}")
        st.write(f"- Collection Name: {settings.collection_name}")

    with col2:
        st.write("**Embedding Settings:**")
        st.write(f"- Model: {settings.embedding_model_name}")
        st.write(f"- Chunk Size: {settings.chunk_size}")
        st.write(f"- Chunk Overlap: {settings.chunk_overlap}")

        st.write("**System Settings:**")
        st.write(f"- Log Level: {settings.log_level}")
        st.write(f"- Debug Mode: {settings.debug}")

    st.info(
        "💡 Settings can be modified via environment variables or .env file",
    )


if __name__ == "__main__":
    main()
