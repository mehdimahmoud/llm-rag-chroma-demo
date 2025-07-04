# RAG System Makefile

.PHONY: help install install-dev clean test test-cov lint format type-check build docs run-demo run-ui

# Default target
help:
	@echo "RAG System - Available Commands:"
	@echo ""
	@echo "Development Setup:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  clean        - Clean build artifacts and cache"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run linting checks (flake8)"
	@echo "  format       - Format code (black + isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  security-check - Run security checks (bandit)"
	@echo "  check-all    - Run all code quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  test-watch   - Run tests in watch mode"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         - Build documentation"
	@echo "  docs-serve   - Serve documentation locally"
	@echo ""
	@echo "Running:"
	@echo "  run-demo     - Run CLI demo"
	@echo "  run-ui       - Run Streamlit UI"
	@echo "  run-interactive - Run interactive CLI mode"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build        - Build package"
	@echo "  dist         - Create distribution"
	@echo "  publish      - Publish to PyPI (if configured)"

# Development Setup
install:
	@echo "Installing production dependencies..."
	pip install -e .

install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

clean: clean-env
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf tests/htmlcov/
	rm -rf tests/coverage.xml
	rm -rf .coverage
	rm -rf .streamlit/
	rm -rf chroma_db/
	rm -rf rag_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

clean-env:
	@echo "Unsetting all environment variables defined in .env file..."
	@if [ -f .env ]; then \
		for var in $$(grep -E '^[A-Z_]+=' .env | cut -d'=' -f1); do \
			echo "Unsetting $$var"; \
			unset $$var; \
		done; \
	else \
		echo "No .env file found, skipping environment variable cleanup"; \
	fi

clean-env-shell:
	@echo "To unset environment variables in your current shell, run:"
	@echo "source clean-env.sh"
	@echo "or"
	@echo "./clean-env.sh"

clean-all: clean clean-env

# Code Quality
lint:
	@echo "Running linting checks..."
	flake8 *.py rag_system/ tests/
	@echo "✅ Linting passed"

autoflake:
	@echo "Removing unused imports and variables..."
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r rag_system/ tests/ *.py
	@echo "✅ Unused imports and variables removed"

format: autoflake
	@echo "Formatting code..."
	black *.py rag_system/ tests/
	isort *.py rag_system/ tests/
	@echo "✅ Code formatted"

type-check:
	@echo "Running type checks on: *.py rag_system/ tests/"
	mypy *.py rag_system/ tests/
	@echo "✅ Type checking passed"

security-check:
	@echo "Running security checks..."
	# Skip B101 (assert_used) as assert statements are standard and acceptable in test files
	bandit -r *.py rag_system/ tests/ -f txt --skip B101
	@echo "✅ Security checks passed"

check-all:
	$(MAKE) autoflake
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security-check
	@echo "✅ All code quality checks passed"

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=rag_system --cov-report=term-missing --cov-report=html

coverage:
	@echo "Running tests and generating coverage.xml in tests/..."
	pytest tests/ -v --cov=rag_system --cov-report=xml:tests/coverage.xml --cov-report=html:tests/htmlcov

test-watch:
	@echo "Running tests in watch mode..."
	pytest tests/ -v -f

# Documentation
docs:
	@echo "Building documentation..."
	# Add documentation build commands here when docs are added
	@echo "Documentation build not yet implemented"

docs-serve:
	@echo "Serving documentation locally..."
	# Add documentation serve commands here when docs are added
	@echo "Documentation serve not yet implemented"

# Running Applications
run-demo:
	@echo "Running RAG system demo..."
	python rag_demo.py

run-ui:
	@echo "Starting Streamlit UI..."
	streamlit run rag_web_interface.py

run-interactive:
	@echo "Running interactive CLI mode..."
	python -m rag_system.cli interactive

# Build & Deploy
build:
	@echo "Building package..."
	python -m build

dist: clean build
	@echo "Creating distribution..."
	python -m build --wheel --sdist

publish: dist
	@echo "Publishing to PyPI..."
	# Add publish commands here when ready for PyPI
	@echo "Publishing not yet configured"

# Development Workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"

quick-test: format lint test
	@echo "✅ Quick test cycle completed"

# Database Management
clear-db:
	@echo "Clearing vector database..."
	python -c "from rag_system.rag_system import RAGSystem; RAGSystem().clear_database()"
	@echo "✅ Database cleared"

# System Information
info:
	@echo "System Information:"
	@echo "Python version: $(shell python --version)"
	@echo "Package version: $(shell python -c "import rag_system; print(rag_system.__version__)")"
	@echo "Data directory: $(shell python -c "from rag_system.core.config import settings; print(settings.data_directory)")"
	@echo "ChromaDB directory: $(shell python -c "from rag_system.core.config import settings; print(settings.chroma_persist_directory)")"



# CI/CD helpers
ci-test: install-dev test-cov lint type-check
	@echo "✅ CI test suite completed"

ci-build: ci-test build
	@echo "✅ CI build completed"

# Docker helpers (for future use)
docker-build:
	@echo "Building Docker image..."
	# Add Docker build commands here when containerization is added
	@echo "Docker build not yet implemented"

docker-run:
	@echo "Running Docker container..."
	# Add Docker run commands here when containerization is added
	@echo "Docker run not yet implemented"

precheck:
	bash .git/hooks/pre-commit

%:
	@: 