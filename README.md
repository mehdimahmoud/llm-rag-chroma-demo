# RAG System

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
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
- **Type Safety**: Comprehensive type hints with MyPy integration
- **Testing**: Comprehensive test suite with enterprise-grade fixtures
- **Code Quality**: Black, isort, flake8, autoflake, and bandit security scanning

## 📋 Requirements

- **Python 3.12+** (required - the project uses Python 3.12 features)
- CUDA-compatible GPU (optional, for faster embedding generation)

## 🛠️ Installation

### Complete Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd llm-rag-chroma-demo

# 2. Create virtual environment with Python 3.12
python3.12 -m venv venv312  # For Python 3.12 (required)
# OR
python -m venv venv  # Uses your default Python (must be 3.12+)

# 3. Activate virtual environment that you have created above
source venv312/bin/activate  # On Linux/Mac (if using venv312)
# OR
source venv/bin/activate     # On Linux/Mac (if using venv)
# OR
venv312\Scripts\activate     # On Windows (if using venv312)
# OR
venv\Scripts\activate        # On Windows (if using venv)

# 4. Install dependencies
make install-dev

# 5. Verify installation
make info
```

### Quick Setup (if you already have a virtual environment)

```bash
# Navigate to your existing project directory
cd llm-rag-chroma-demo

# Activate your existing virtual environment (must be Python 3.12+)
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
make install-dev
```

## ⚙️ Configuration

**Configuration is optional** - the system works with default settings. You can configure it anytime after installation:

### Environment Variables

Create a `.env` file in the project root by copying the template:

```bash
cp .env.default .env
```

Then edit the `.env` file to set your actual values, especially the OpenAI API key:

```env
# Project settings
APP_NAME=RAG System
# Logging
LOG_LEVEL=INFO
# Langchain settings
SUPPORTED_FILE_TYPES=[".pdf", ".txt", ".docx", ".md", ".csv", ".xlsx"]
CHUNK_SIZE=120
CHUNK_OVERLAP=24
# ChromaDB settings
CHROMA_PERSIST_DIRECTORY=chroma_db
CHROMA_TELEMETRY_ENABLED=false
# Embedding model
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
# Openai
OPENAI_API_KEY="your actual openai api key here"
OPENAI_MODEL_NAME="gpt-4o-mini"
```

> **Note:** If you want to fully reset your environment variables in your current shell, run:
> ```bash
> source clean-env.sh
> ```
> This ensures no old or conflicting variables interfere with your run.

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

# Run specific test file
pytest tests/test_ingestion.py -v

# Run tests with specific marker
pytest -m "slow" -v
```

## 🔧 Development

### Code Quality and Type Safety

This project maintains enterprise-grade code quality with:

- **Comprehensive Type Annotations**: All functions, methods, and variables have type hints
- **Static Type Checking**: MyPy integration ensures type safety across the codebase
- **Code Formatting**: Black and isort ensure consistent code style
- **Linting**: Flake8 and autoflake maintain code quality
- **Security Scanning**: Bandit identifies potential security issues
- **Testing**: Comprehensive test suite with clean fixtures

### Code Quality

```bash
# Format code (black + isort)
make format

# Run linting (flake8 + autoflake)
make lint

# Type checking (mypy)
make type-check

# Security scanning (bandit)
make security-check

# All quality checks
make check-all

# Clean unused imports and variables
make clean-imports

# Pre-commit validation (runs automatically on staged files)
# The custom pre-commit hook runs the same tools as make check-all
# but only on staged files during git commit
```

### Development Workflow

```bash
# Complete development setup
make dev-setup

# Clean build artifacts
make clean

# (Recommended) Unset all environment variables from .env in your current shell
source clean-env.sh

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
   export CHROMA_PERSIST_DIRECTORY=chroma_db
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
- **Follow comprehensive type hints throughout**
- **Raise exceptions rather than returning error strings**
- **Never commit `.env` files** - use `.env.default` as template
- **Run `make check-all` before committing**
- **Pre-commit hooks run automatically** on staged files during commit

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
