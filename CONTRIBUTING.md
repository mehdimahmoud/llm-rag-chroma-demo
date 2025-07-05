# Contributing to RAG System

Thank you for considering contributing to this project! This guide will help you get set up, develop features, and submit high-quality pull requests.

---

## 1. Getting Started

### Prerequisites
- **Python 3.12+** (required - the project uses Python 3.12 features)
- Git
- Make (for development workflow)

### Clone the Repository
```bash
git clone <repo-url>
cd <repo-directory>
```

### Set Up Your Environment
- **Create and activate a virtual environment with Python 3.12:**
  ```bash
  python3.12 -m venv venv312
  source venv312/bin/activate  # or .\venv312\Scripts\activate on Windows
  ```
- **Install all development dependencies:**
  ```bash
  make install-dev
  ```
- **Set up your environment configuration:**
  ```bash
  cp .env.default .env
  # Edit .env with your actual API keys and settings
  ```
- **(Recommended) Clean environment variables before running tests:**
  ```bash
  source clean-env.sh
  ```
  This ensures your environment is clean and avoids issues with stale or conflicting variables.

---

## 2. Development Workflow

### Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### Make Your Changes
- Write code and tests following our coding standards
- **Always add type hints** to all functions, methods, and variables
- Keep commits focused and descriptive

### Code Quality Standards

#### Type Safety
- **All code must have comprehensive type annotations**
- Use `typing` module for complex types
- Run type checking: `make type-check`
- Fix all mypy errors before committing

#### Code Formatting and Linting
- **Format code:**
  ```bash
  make format  # Runs black and isort
  ```
- **Run linting:**
  ```bash
  make lint    # Runs flake8 and autoflake
  ```
- **Type checking:**
  ```bash
  make type-check  # Runs mypy
  ```
- **Security scanning:**
  ```bash
  make security-check  # Runs bandit
  ```
- **Run all quality checks:**
  ```bash
  make check-all
  ```
- **Pre-commit validation** (runs automatically on staged files):
  ```bash
  # The custom pre-commit hook runs the same tools as make check-all
  # but only on staged files during git commit
  # Note: CI runs these checks independently, so the hook is for developer convenience
  # Skip in exceptional cases: git commit --no-verify -m "message"
  ```

#### Testing
- **Run tests:**
  ```bash
  make test
  ```
- **Run tests with coverage:**
  ```bash
  make test-cov
  ```

### Commit Your Changes
- **All quality checks must pass before committing**
- **Pre-commit hooks run automatically** on staged files during commit (developer convenience)
- The custom pre-commit hook runs: black, isort, flake8, mypy, and bandit
- **You can run the same checks manually** before staging: `make check-all`
- **CI runs `make check-all` independently** to ensure code quality
- **Skip pre-commit hooks in exceptional cases**: `git commit --no-verify -m "message"`
- Use descriptive commit messages following conventional commits
- Example: `feat: add new document processor for CSV files`

---

## 3. Before Submitting a Pull Request (PR)
- **Sync with main branch:**
  ```bash
  git fetch origin
  git rebase origin/main
  # or
  git merge origin/main
  ```
- **Run all checks again:**
  ```bash
  make check-all
  make test
  ```
- **Push your branch:**
  ```bash
  git push origin feature/your-feature-name
  ```

---

## 4. Submitting a Pull Request
- Open a PR from your feature branch to `main`
- Fill in the PR template, describe your changes, and link the relevant ticket/issue (e.g., "Closes #123")
- Ensure all checks pass and address any review comments
- **All PRs must pass:**
  - Code formatting (black, isort)
  - Linting (flake8, autoflake)
  - Type checking (mypy)
  - Security scanning (bandit)
  - Tests (pytest)
- **Pre-commit hooks run automatically** on staged files during commit

---

## 5. After Merge
- Move the ticket/issue to "Done" or "Closed" in your project management tool

---

## 6. Coding Standards

### Type Annotations
- **All functions must have return type annotations**
- **All parameters must have type hints**
- **Use `Any` sparingly - prefer specific types**
- **Use `Optional[T]` for nullable values**
- **Use `Union[T1, T2]` or `T1 | T2` for multiple types**

```python
# Good
def process_documents(docs: list[Document], settings: Settings) -> list[Document]:
    """Process documents and return processed versions."""
    pass

# Avoid
def process_documents(docs, settings):  # No type hints
    pass
```

### Error Handling
- **Raise exceptions rather than returning error strings**
- **Use specific exception types**
- **Include meaningful error messages**

```python
# Good
if not api_key:
    raise ValueError("OpenAI API key is required")

# Avoid
if not api_key:
    return "Error: API key missing"
```

### Testing
- **Write tests for all new functionality**
- **Use descriptive test names**
- **Test both success and failure cases**
- **Use fixtures for common setup**

### Documentation
- **Add docstrings to all public functions and classes**
- **Update README.md for user-facing changes**
- **Update CONTRIBUTING.md for development workflow changes**

---

## 7. Additional Tips
- Keep PRs small and focused for easier review
- Write clear commit messages following conventional commits
- Add or update documentation as needed
- If you have questions, open an issue or ask in the project chat
- **Never commit `.env` files** - they contain sensitive information
- **Always run `make check-all` before pushing**
- **Use `--no-verify` sparingly** - only for exceptional cases when pre-commit hooks need to be bypassed

---

## 8. Environment and Security

### Environment Variables
- **Never commit `.env` files** - they contain API keys and sensitive data
- **Use `.env.default` as a template** for required environment variables
- **The `.env` file is already in `.gitignore`** - keep it that way

### API Keys and Secrets
- **Never hardcode API keys in source code**
- **Use environment variables for all sensitive configuration**
- **Test with mock data when possible**

---

Thank you for helping make this project better!