# Contributing to g-sheet-mcp

Thank you for considering a contribution! This guide will help you get started.

---

## Development Setup

```bash
# Clone the repo
git clone https://github.com/mariadb-RupeshBiswas/google-sheets-mcp.git
cd google-sheets-mcp

# Install all dependencies including dev extras
uv sync --extra dev

# Authenticate for integration tests
gcloud auth login --enable-gdrive-access --update-adc
```

---

## Running Tests

```bash
# Unit tests only (fast, no API calls)
uv run pytest tests/ --ignore=tests/test_integration.py

# With coverage
uv run pytest --cov=src/g_sheet_mcp --cov-report=term-missing

# Integration tests (requires auth + test spreadsheet)
cp .env.example .env
# Edit .env and add your TEST_SPREADSHEET_ID
INTEGRATION=1 TEST_SPREADSHEET_ID=your_test_spreadsheet_id uv run pytest tests/test_integration.py -v

# All tests
INTEGRATION=1 TEST_SPREADSHEET_ID=your_test_spreadsheet_id uv run pytest
```

---

## Code Quality

### Linting and Formatting

```bash
# Run ruff linter
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/

# Refresh the lockfile if dependencies change
uv lock
```

### Pre-commit Checks

Before submitting a PR, ensure:
- ✅ All tests pass
- ✅ No linting errors
- ✅ Type hints are correct
- ✅ New code has test coverage
- ✅ Public examples stay sanitized (no real sheet IDs, emails, or customer/internal data)

---

## Project Structure

```
google-sheets-mcp/
├── src/g_sheet_mcp/
│   ├── __init__.py       # Package version
│   ├── auth.py           # ADC authentication
│   ├── models.py         # Pydantic models
│   ├── sheets.py         # SheetsClient wrapper
│   └── server.py         # FastMCP server
├── tests/
│   ├── test_auth.py      # Auth unit tests
│   ├── test_sheets.py    # Sheets unit tests
│   ├── test_server.py    # Server unit tests
│   └── test_integration.py  # Live API tests
├── docs/                 # Documentation
├── agents/               # LLM instructions
└── mcp-config-examples/  # Editor configs
```

---

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Write Tests First (TDD)

Add tests to the appropriate file in `tests/`:

```python
def test_your_new_feature(client):
    result = client.your_method()
    assert result.something == expected
```

### 3. Implement the Feature

- Follow existing code style
- Add type hints to all functions
- Add docstrings for public methods
- Handle errors gracefully

### 4. Update Documentation

- Update `README.md` if adding user-facing features
- Update `CHANGELOG.md` with your changes
- Add examples to `agents/EXAMPLES.md` if relevant
- Keep all examples generic and safe for a public repository

### 4a. Follow the versioning policy

- This project uses **PEP 440-compliant Semantic Versioning**
- Read **[docs/VERSIONING.md](docs/VERSIONING.md)** before choosing the next release number
- Keep `pyproject.toml` and `src/g_sheet_mcp/__init__.py` in sync when cutting a new package release
- Do not bump the package version for docs-only or CI-only changes unless you intentionally want a new PyPI release

### 5. Commit with Conventional Commits

```bash
git commit -m "feat: add new feature X"
git commit -m "fix: resolve bug in Y"
git commit -m "docs: update installation guide"
git commit -m "test: add coverage for Z"
git commit -m "chore: update dependencies"
```

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

**Types:**
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `test:` — Adding/updating tests
- `refactor:` — Code change that neither fixes a bug nor adds a feature
- `chore:` — Maintenance tasks
- `perf:` — Performance improvement
- `build:` — Build system or dependencies

**Examples:**
```
feat(sheets): add pagination support for large datasets
fix(auth): handle expired credentials gracefully
docs(readme): clarify installation steps
test(integration): add test for URL handling
```

---

## Pull Request Process

1. **Fork the repo** and create your branch from `main`
2. **Write tests** for your changes
3. **Ensure all tests pass** locally
4. **Update documentation** as needed
5. **Submit a PR** with:
   - Clear title following conventional commits
   - Description of what changed and why
   - Link to any related issues

### PR Checklist

- [ ] Tests pass: `uv run pytest`
- [ ] Linting passes: `uv run ruff check src/ tests/`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Documentation updated
- [ ] `CHANGELOG.md` updated
- [ ] Version bump follows `docs/VERSIONING.md` if a new package release is intended
- [ ] Commit messages follow conventional format

---

## Adding New MCP Tools

To add a new tool to the server:

### 1. Add the method to `SheetsClient` (sheets.py)

```python
def your_new_method(
    self,
    spreadsheet_id: str,
    param: str,
) -> YourReturnType:
    """Your method description.
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID or full URL.
        param: Description of parameter.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: If validation fails.
    """
    spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
    # Your implementation
```

### 2. Add the MCP tool (server.py)

```python
@mcp.tool()
def your_tool_name(
    spreadsheet_id: str,
    param: str,
) -> dict[str, Any]:
    """Tool description for LLM."""
    client = _get_client()
    result = client.your_new_method(spreadsheet_id, param)
    return result.model_dump()
```

### 3. Add tests

```python
# Unit test (test_sheets.py)
def test_your_new_method(mock_service):
    client = SheetsClient(...)
    result = client.your_new_method(...)
    assert result.something == expected

# Integration test (test_integration.py)
def test_your_tool_integration(client):
    result = client.your_new_method(SAMPLE_ID, ...)
    assert result.field == value
```

### 4. Update documentation

- Add to feature table in `README.md`
- Add example to `agents/EXAMPLES.md`
- Document in `agents/AGENT_INSTRUCTIONS.md`

---

## Reporting Bugs

Use the GitHub issue tracker:

**Include:**
- Python version
- OS version
- Error message/stack trace
- Steps to reproduce
- Expected vs actual behavior

**Example:**
```markdown
**Bug:** `read_sheet` fails with spaces in sheet name

**Environment:**
- Python 3.11.5
- macOS 14.2

**Steps:**
1. Call `read_sheet(id, "Example Sheet 1")`
2. Error: ...

**Expected:** Should read the sheet
**Actual:** Raises ValueError
```

---

## Feature Requests

Use GitHub issues with the `enhancement` label.

**Include:**
- Use case / motivation
- Proposed API / interface
- Example usage
- Alternatives considered

---

## Questions?

- Check the [documentation](docs/)
- Search existing [GitHub issues](https://github.com/mariadb-RupeshBiswas/google-sheets-mcp/issues)
- Open a new issue for discussion

---

## Code of Conduct

- Be respectful and professional
- Provide constructive feedback
- Help others learn and grow
- Focus on what's best for the project

Thank you for contributing! 🎉
