# 📦 Publishing to PyPI (Optional)

Publishing to PyPI enables the simplest install path:

```bash
uvx g-sheet-mcp
```

This is optional. The project already works from:

- a local clone with `uv sync` + `uv run`
- GitHub with `uvx --from git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp`
- a local path with `uvx --from /absolute/path/to/google-sheets-mcp`

---

## Before publishing

### 1. Confirm project metadata

The package metadata already points to the public repo:

- Repository: `https://github.com/mariadb-RupeshBiswas/google-sheets-mcp`
- Package name: `g-sheet-mcp`
- CLI entry point: `g-sheet-mcp`

When cutting a release, update both version locations:

- `pyproject.toml`
- `src/g_sheet_mcp/__init__.py`

### 2. Refresh the lockfile and build artifacts

```bash
uv lock
uv build
```

### 3. Smoke-test the built package

```bash
uvx --from dist/*.whl g-sheet-mcp --help
```

### 4. Run the release checks

```bash
uv run ruff check src tests
uv run mypy src
uv run pytest tests/ --ignore=tests/test_integration.py -q
```

---

## Option A — Manual publish with `uv`

Create a PyPI project for `g-sheet-mcp`, then publish with an API token:

```bash
export UV_PUBLISH_TOKEN=pypi-...
uv build
uv publish
```

Notes:

- Use an environment variable or keyring-backed auth — do not hardcode tokens in repo files
- `uv publish --dry-run` is useful before the real upload

---

## Option B — Trusted publishing via GitHub Actions (recommended)

This repo can publish without storing a PyPI token if you configure PyPI trusted publishing.

### PyPI setup

1. Create the `g-sheet-mcp` project on PyPI
2. In PyPI, add a **Trusted Publisher** for:
   - **Owner:** `mariadb-RupeshBiswas`
   - **Repository:** `google-sheets-mcp`
   - **Workflow:** `publish.yml`
3. Push a version tag such as `v0.1.0`

The matching workflow can live at `.github/workflows/publish.yml` and publish with `uv publish --trusted-publishing=always`.

---

## GitHub release flow

1. Update `CHANGELOG.md`
2. Bump `version` in `pyproject.toml` and `src/g_sheet_mcp/__init__.py`
3. Run:

```bash
uv lock
uv build
uv run ruff check src tests
uv run mypy src
uv run pytest tests/ --ignore=tests/test_integration.py -q
```

4. Commit the release changes
5. Create a tag:

```bash
git tag v0.1.0
```

6. Push commits and tags:

```bash
git push origin main --tags
```

7. Publish manually with `uv publish` or let GitHub Actions handle it

---

## Versioning strategy

Follow [Semantic Versioning](https://semver.org/):

- **0.1.0** — Initial public release
- **0.1.1** — Bug fixes
- **0.2.0** — New backward-compatible features
- **1.0.0** — Stable API / docs / release workflow

---

## Usage after publishing

### Install or run

```bash
# Ephemeral run with uvx
uvx g-sheet-mcp

# Persistent install
pipx install g-sheet-mcp
```

### Editor configs get simpler

**Before (local clone):**

```json
{
  "command": "uv",
  "args": ["--directory", "/absolute/path/to/google-sheets-mcp", "run", "g-sheet-mcp"]
}
```

**After (PyPI):**

```json
{
  "command": "uvx",
  "args": ["g-sheet-mcp"]
}
```

---

## Do you need to publish?

**Probably no, if:**

- you are the only user
- GitHub + `uvx --from git+...` is enough
- you want to avoid PyPI maintenance

**Probably yes, if:**

- you want the shortest install path (`uvx g-sheet-mcp`)
- you want simpler editor setup snippets
- you want a standard public package page for the project

The project is fully functional even before PyPI publishing.
