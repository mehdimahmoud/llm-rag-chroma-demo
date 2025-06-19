# RAG-based AI Assistant with ChromaDB and OpenAI

This project demonstrates how to build a simple Retrieval-Augmented Generation (RAG) pipeline using ChromaDB and OpenAI's API.

## Features
- Load and chunk documents.
- Create and store embeddings in ChromaDB.
- Query documents via semantic search.
- Use OpenAI or local LLM to generate responses.

## Stack

- Python
- ChromaDB
- OpenAI (or SentenceTransformers)
- Streamlit (optional UI)

## Usage
1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate` (on Windows: `source venv/Scripts/activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. Ingest documents: `python ingest_documents.py`
5. Run the query engine: `python query_engine.py`
6. Launch Streamlit UI: `streamlit run app_streamlit.py`

