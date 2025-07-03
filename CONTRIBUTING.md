# Contributing to RAG System

Thank you for considering contributing to this project! This guide will help you get set up, develop features, and submit high-quality pull requests.

---

## 1. Getting Started

### Clone the Repository
```bash
git clone <repo-url>
cd <repo-directory>
```

### Set Up Your Environment
- **Create and activate a virtual environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # or .\venv\Scripts\activate on Windows
  ```
- **Install all development dependencies and pre-commit hooks:**
  ```bash
  make install-dev
  ```
- **(Recommended) Unset all environment variables from .env in your current shell before running the demo or tests:**
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
- Write code and tests.
- Keep commits focused and descriptive.

### Run Code Quality Checks and Tests
- Format and lint:
  ```bash
  make format
  make lint
  ```
- Type check:
  ```bash
  make type-check
  ```
- Run tests:
  ```bash
  make test
  ```
- Or run all checks at once:
  ```bash
  make check-all
  ```
- (Optional) Run pre-commit hooks on all files:
  ```bash
  make pre-commit-run
  ```

### Commit Your Changes
- Pre-commit hooks will run automatically on staged files.
- Fix any issues reported by hooks before pushing.

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
- Open a PR from your feature branch to `main`.
- Fill in the PR template, describe your changes, and link the relevant ticket/issue (e.g., "Closes #123").
- Ensure all checks pass and address any review comments.

---

## 5. After Merge
- Move the ticket/issue to "Done" or "Closed" in your project management tool.

---

## 6. Additional Tips
- Keep PRs small and focused for easier review.
- Write clear commit messages.
- Add or update documentation as needed.
- If you have questions, open an issue or ask in the project chat.

---

Thank you for helping make this project better!