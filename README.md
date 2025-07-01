# RAG System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A production-ready **Retrieval-Augmented Generation (RAG)** system built with LangChain and ChromaDB.

## 📚 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#️-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Project Structure](#️-project-structure)
- [Testing](#-testing)
- [Development](#-development)
- [Monitoring](#-monitoring)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Support](#-support)

## 🚀 Features

- **Multi-format Document Support**: PDF, TXT, DOCX, MD, CSV, XLSX
- **Advanced Text Processing**: Intelligent chunking with configurable overlap
- **Vector Storage**: ChromaDB integration with persistent storage
- **Embedding Generation**: Sentence Transformers with customizable models
- **Dual Interface**: Command-line and Streamlit web UI
- **Structured Logging**: Logging with correlation IDs
- **Type Safety**: Full type hints and MyPy integration
- **Testing**: Comprehensive test suite with 80%+ coverage
- **Code Quality**: Black, isort, flake8, and pre-commit hooks

## 📋 Requirements

- Python 3.8+ (recommended: Python 3.9 or 3.10 for best compatibility)
- CUDA-compatible GPU (optional, for faster embedding generation)

## 🛠️ Installation

### Complete Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd llm-rag-chroma-demo

# 2. Create virtual environment with Python 3.8+
python3.8 -m venv venv38  # For Python 3.8
# OR
python3.9 -m venv venv39  # For Python 3.9 (recommended)
# OR
python3.10 -m venv venv310 # For Python 3.10
# OR
python3.12 -m venv venv # For Python 3.12
# OR
python -m venv venv  # Uses your default Python (3.8+)

# 3. Activate virtual environment that you have created above
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# 4. Install dependencies
make install-dev

# 5. Verify installation
make info
```

### Quick Setup (if you already have a virtual environment)

```bash
# Navigate to your existing project directory
cd llm-rag-chroma-demo

# Activate your existing virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
make install-dev
```

## ⚙️ Configuration

**Configuration is optional** - the system works with default settings. You can configure it anytime after installation:

### Environment Variables

```bash
# Set environment variables
export APP_NAME="My RAG System"
export DEBUG=true
export CHUNK_SIZE=1000
export CHUNK_OVERLAP=200
export EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"
export LOG_LEVEL="INFO"
```

### Or create a `.env` file

```env
APP_NAME=My RAG System
DEBUG=true
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
LOG_LEVEL=INFO
```

## 🎯 Usage

### Quick Start

```bash
# Run the demo
make run-demo

# Or start the web interface
make run-ui
```

### Command Line Interface

```bash
# Interactive mode
rag-demo interactive

# Ingest all documents
rag-demo ingest

# Query the system
rag-demo query "What are the HR policies?"

# Get system statistics
rag-demo stats

# Clear the database
rag-demo clear
```

### Web Interface

```bash
# Start Streamlit UI
make run-ui
# or
streamlit run rag_web_interface.py
```

### Programmatic Usage

```python
from rag_system import RAGSystem

# Initialize the system
rag = RAGSystem()

# Ingest documents
stats = rag.ingest_documents()
print(f"Processed {stats['documents_stored']} documents")

# Query the system
results = rag.query("What are the vacation policies?")
for doc in results:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:200]}...")
```

## 🏗️ Project Structure

```
rag-system/
├── rag_system/                 # Main package
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   └── logging.py         # Structured logging
│   ├── ingestion/             # Document processing
│   │   ├── document_loader.py # Multi-format document loading
│   │   ├── text_processor.py  # Text chunking and embedding
│   │   └── vector_store.py    # ChromaDB integration
│   ├── ui/                    # User interfaces
│   │   └── streamlit_app.py   # Streamlit web UI
│   ├── cli.py                 # Command-line interface
│   └── rag_system.py          # Main orchestrator
├── tests/                     # Test suite
│   ├── test_core_config.py    # Configuration tests
│   └── test_ingestion.py      # Ingestion component tests
├── data/                      # Document storage
├── rag_demo.py               # Demo script
├── rag_web_interface.py      # Web interface
├── pyproject.toml             # Project configuration
├── Makefile                   # Development workflow
└── README.md                  # This file
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests in watch mode
make test-watch

# Quick test cycle (format + lint + test)
make quick-test
```

## 🔧 Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# All quality checks
make check-all
```

### Development Workflow

```bash
# Complete development setup
make dev-setup

# Clean build artifacts
make clean

# Build package
make build

# System information
make info
```

## 📊 Monitoring

The system includes comprehensive logging:

```python
import structlog

# Structured logging with correlation IDs
logger = structlog.get_logger(__name__)
logger.info("Processing document",
           document_id="doc_123",
           file_type="pdf",
           chunk_count=15)
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
   ```bash
   export PRODUCTION=true
   export LOG_LEVEL=WARNING
   export CHROMA_PERSIST_DIRECTORY=/data/chroma
   ```

2. **Install Production Dependencies**:
   ```bash
   make install
   ```

3. **Initialize System**:
   ```bash
   rag-demo ingest
   ```

### Docker (Future)

```bash
# Build image
make docker-build

# Run container
make docker-run
```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and best practices.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run quality checks: `make check-all`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Use snake_case for files and functions
- Use PascalCase for classes
- Write comprehensive docstrings
- Maintain 80%+ test coverage
- Follow type hints throughout

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) for embeddings
- [Streamlit](https://streamlit.io/) for the web interface

## 📞 Support

For support and questions:

- Create an [issue](https://github.com/your-repo/issues)
- Check the [documentation](docs/)
- Review the [examples](examples/)

---

**Built with ❤️ for production AI applications**
