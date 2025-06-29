# Enterprise-Grade Development Makefile
# Best practices for team development

.PHONY: help install test test-unit test-integration test-e2e test-coverage lint format clean docs ci cd

# Default target
help:
	@echo "🚀 Enterprise-Grade Development Commands"
	@echo "========================================"
	@echo "📦 Setup & Installation:"
	@echo "  install          Install all dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             Run all tests with coverage"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e         Run end-to-end tests only"
	@echo "  test-coverage    Generate coverage report"
	@echo "  test-fast        Run tests without coverage (faster)"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  lint             Run all linting tools"
	@echo "  format           Format code with black and isort"
	@echo "  type-check       Run type checking with mypy"
	@echo "  security         Run security checks with bandit"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs             Build documentation"
	@echo "  docs-serve       Serve documentation locally"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean            Clean all generated files"
	@echo "  clean-cache      Clean Python cache files"
	@echo ""
	@echo "🚀 CI/CD:"
	@echo "  ci               Run CI pipeline locally"
	@echo "  cd               Run CD pipeline locally"

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pre-commit install
	@echo "✅ Development setup complete!"

# Testing
test:
	@echo "🧪 Running all tests with coverage..."
	pytest --cov=src --cov-report=html:htmlcov --cov-report=xml:coverage.xml --cov-report=term-missing --cov-fail-under=80
	@echo "✅ All tests completed!"

test-unit:
	@echo "🧪 Running unit tests..."
	pytest -m "unit" --cov=src --cov-report=term-missing

test-integration:
	@echo "🧪 Running integration tests..."
	pytest -m "integration" --cov=src --cov-report=term-missing

test-e2e:
	@echo "🧪 Running end-to-end tests..."
	pytest -m "e2e" --cov=src --cov-report=term-missing

test-coverage:
	@echo "📊 Generating coverage report..."
	pytest --cov=src --cov-report=html:htmlcov --cov-report=xml:coverage.xml --cov-report=term-missing
	@echo "📈 Coverage report generated in htmlcov/"

test-fast:
	@echo "⚡ Running tests without coverage..."
	pytest --no-cov

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 src tests
	black --check src tests
	isort --check-only src tests
	@echo "✅ Linting passed!"

format:
	@echo "🎨 Formatting code..."
	black src tests
	isort src tests
	@echo "✅ Code formatted!"

type-check:
	@echo "🔍 Running type checks..."
	mypy src
	@echo "✅ Type checking passed!"

security:
	@echo "🔒 Running security checks..."
	bandit -r src
	@echo "✅ Security checks passed!"

# Documentation
docs:
	@echo "📚 Building documentation..."
	cd docs && make html
	@echo "✅ Documentation built!"

docs-serve:
	@echo "🌐 Serving documentation..."
	cd docs/_build/html && python -m http.server 8000

# Maintenance
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .mypy_cache/
	@echo "✅ Cleanup complete!"

clean-cache:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cache cleanup complete!"

# CI/CD
ci:
	@echo "🚀 Running CI pipeline..."
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test
	@echo "✅ CI pipeline passed!"

cd:
	@echo "🚀 Running CD pipeline..."
	$(MAKE) ci
	$(MAKE) docs
	@echo "✅ CD pipeline passed!"

# Development helpers
dev-setup: install-dev
	@echo "🎯 Development environment ready!"
	@echo "Run 'make test' to start testing"
	@echo "Run 'make help' to see all available commands"

# Quick development cycle
dev-cycle: format lint test-fast
	@echo "🔄 Development cycle complete!"

# Performance testing
benchmark:
	@echo "⚡ Running performance benchmarks..."
	pytest --benchmark-only

# Test specific data directories
test-hr-policy:
	@echo "🧪 Testing with HR policy data..."
	python tests/run_menu_tests.py --data-dir tests/data/hr_policy

# Generate test report
test-report:
	@echo "📊 Generating comprehensive test report..."
	pytest --html=reports/pytest_report.html --self-contained-html --cov=src --cov-report=html:htmlcov
	@echo "📈 Report generated in reports/ and htmlcov/" 