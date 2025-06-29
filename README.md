# LLM RAG ChromaDB Demo

A comprehensive RAG (Retrieval-Augmented Generation) system with ChromaDB vector store, featuring enterprise-grade testing infrastructure and development workflows.

## 🚀 Features

- **Document Processing**: Support for PDF, DOCX, TXT, and Excel files
- **Text Extraction**: Intelligent text extraction with metadata preservation
- **Chunking**: Configurable text chunking strategies
- **Embeddings**: SentenceTransformers integration for vector embeddings
- **Vector Store**: ChromaDB for efficient similarity search
- **Menu System**: Interactive CLI for document management
- **Enterprise Testing**: Comprehensive test coverage with CI/CD

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd llm-rag-chroma-demo

# Install dependencies
make install

# Setup development environment
make install-dev
```

## 🧪 Testing Infrastructure

This project includes a comprehensive, enterprise-grade testing infrastructure designed to teach students professional development practices.

### Test Types

- **Unit Tests** (`@pytest.mark.unit`): Test individual components in isolation
- **Integration Tests** (`@pytest.mark.integration`): Test component interactions
- **End-to-End Tests** (`@pytest.mark.e2e`): Test complete workflows
- **Performance Tests** (`@pytest.mark.benchmark`): Test system performance

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Run tests without coverage (faster)
make test-fast

# Run tests with specific data directory
python run_menu_tests.py --data-dir tests/data/hr_policy

# Generate coverage report
make test-coverage
```

### Test Coverage

The project maintains **80% minimum code coverage** with comprehensive testing of:

- ✅ **22 Menu Workflow Scenarios**: All possible menu combinations
- ✅ **File Processing**: PDF, DOCX, TXT, Excel handling
- ✅ **Text Extraction**: Various file formats and edge cases
- ✅ **Chunking Strategies**: Different chunking approaches
- ✅ **Embedding Generation**: Vector creation and storage
- ✅ **Database Operations**: CRUD operations on ChromaDB
- ✅ **Error Handling**: Invalid inputs, file errors, network issues
- ✅ **Performance**: Response times and resource usage

## 🔍 Code Quality

### Linting and Formatting
```bash
# Check code quality
make lint

# Format code
make format

# Type checking
make type-check

# Security checks
make security
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security analysis

## 🚀 CI/CD Pipeline

### GitHub Actions
The project includes a comprehensive CI/CD pipeline with:

1. **Quality Checks**: Linting, type checking, security analysis
2. **Unit Tests**: Fast unit test execution
3. **Integration Tests**: Component interaction testing
4. **End-to-End Tests**: Complete workflow validation
5. **Coverage Reporting**: Code coverage analysis
6. **Performance Tests**: Benchmark execution
7. **Test Summary**: Comprehensive results reporting

### Coverage Reporting
- **HTML Reports**: Detailed coverage reports in `htmlcov/`
- **XML Reports**: CI/CD integration with coverage.xml
- **Codecov Integration**: GitHub coverage badges
- **Coverage Threshold**: 80% minimum requirement

## 📊 Development Workflows

### Daily Development Cycle
```bash
# Quick development cycle
make dev-cycle

# Full CI pipeline locally
make ci

# Complete CD pipeline
make cd
```

### Testing Different Data Sets
```bash
# Test with HR policy data
make test-hr-policy

# Test with custom data directory
python run_menu_tests.py --data-dir path/to/your/data

# List available test data directories
python run_menu_tests.py --list
```

## 📚 Documentation

### Project Structure
```
llm-rag-chroma-demo/
├── src/                    # Source code
│   ├── ingestion/         # Document ingestion system
│   ├── chroma/            # Vector store integration
│   ├── embeddings/        # Embedding generation
│   └── logutils/          # Logging utilities
├── tests/                 # Test files
│   ├── data/             # Test data directories
│   └── test_*.py         # Test modules
├── docs/                  # Documentation
├── .github/workflows/     # CI/CD pipelines
├── Makefile              # Development commands
├── pytest.ini           # Test configuration
├── requirements.txt      # Dependencies
└── README.md            # This file
```

### Key Components

#### Menu System
- **IngestionMenuOrchestrator**: Main menu controller
- **ConsoleUserInterface**: User interaction layer
- **Command Pattern**: Modular command execution

#### Document Processing
- **DocumentLoader**: File discovery and loading
- **TextExtractorFactory**: Format-specific extraction
- **TextChunker**: Text segmentation strategies

#### Vector Operations
- **ChromaDBVectorStore**: Vector database operations
- **SentenceTransformerEmbeddingGenerator**: Embedding creation

## 🎯 Learning Objectives

This project demonstrates enterprise-grade development practices:

### Testing Best Practices
- **Test-Driven Development (TDD)**: Write tests first
- **Comprehensive Coverage**: Test all code paths
- **Test Isolation**: Independent test execution
- **Mocking**: Isolate components for testing
- **Performance Testing**: Monitor system performance

### Code Quality
- **Consistent Formatting**: Black and isort
- **Type Safety**: MyPy type checking
- **Security**: Bandit security analysis
- **Documentation**: Comprehensive docstrings

### CI/CD Practices
- **Automated Testing**: GitHub Actions integration
- **Quality Gates**: Coverage and quality thresholds
- **Artifact Management**: Test result storage
- **Deployment Automation**: Streamlined releases

### Team Development
- **Pre-commit Hooks**: Quality enforcement
- **Standardized Workflows**: Makefile commands
- **Code Reviews**: Pull request requirements
- **Documentation**: Comprehensive README

## 🔧 Configuration

### Environment Variables
```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=documents

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Test Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
addopts = --cov=src --cov-report=html --cov-fail-under=80
markers = unit, integration, e2e, benchmark
```

## 📈 Performance

### Benchmarks
- **Document Processing**: ~100 documents/minute
- **Text Extraction**: ~50MB/minute
- **Embedding Generation**: ~1000 chunks/minute
- **Vector Search**: <100ms response time

### Resource Usage
- **Memory**: ~2GB for typical workloads
- **Storage**: ~1GB per 10,000 documents
- **CPU**: Multi-threaded processing

## 🤝 Contributing

### Development Setup
```bash
# 1. Fork and clone the repository
git clone <your-fork-url>
cd llm-rag-chroma-demo

# 2. Setup development environment
make dev-setup

# 3. Create feature branch
git checkout -b feature/your-feature

# 4. Make changes and test
make dev-cycle

# 5. Commit with conventional commits
git commit -m "feat: add new feature"

# 6. Push and create pull request
git push origin feature/your-feature
```

### Commit Convention
```
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: test additions/changes
chore: maintenance tasks
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ChromaDB**: Vector database technology
- **SentenceTransformers**: Embedding models
- **pypdf**: PDF processing
- **python-docx**: DOCX processing
- **openpyxl**: Excel processing

---

**For Students**: This project demonstrates real-world software development practices used in enterprise environments. Focus on understanding the testing strategies, code quality practices, and CI/CD workflows as these are essential skills for professional development.