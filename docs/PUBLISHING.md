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

Follow **[docs/VERSIONING.md](VERSIONING.md)** for the release policy that determines whether the next version should be a patch, minor, or major bump.

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

## Option B — Publish from GitHub Actions with a PyPI token

This repo now supports publishing from the GitHub `pypi` environment using the environment secret:

- `PYPI__TOKEN__`

The workflow is intentionally restricted so publishing only runs from **protected `main`**.
It starts on pushes to `main` and manual `workflow_dispatch`, and skips cleanly when the current
version is already fully published on PyPI.

### GitHub setup

1. Create the `g-sheet-mcp` project on PyPI
2. Add the PyPI API token as the `PYPI__TOKEN__` secret in the GitHub `pypi` environment
3. Protect the `main` branch
4. Push the release commit to `main` or run the `Publish` workflow manually from `main`

The workflow in `.github/workflows/publish.yml` builds with `uv build`, checks PyPI for the
exact built filenames, and uploads with `uv publish --check-url https://pypi.org/simple/` when
that version is not already fully published.

### GitHub sidebar note: Releases vs Packages vs PyPI

- Publishing to **PyPI** does **not** populate the **Packages** section in the GitHub repo sidebar
- GitHub **Packages** only shows artifacts published to GitHub's own package registries
- GitHub **Releases** are also separate — they appear only when you create a GitHub Release object from a tag

So it is normal for this repo to have a PyPI package while the GitHub **Packages** section remains empty.

### What happens on every push to `main`

- If the built artifacts for the current version do **not** exist on PyPI, the workflow publishes them
- If that version is **already** fully published, the workflow logs a skip message and exits cleanly
- If PyPI contains only part of the release, `uv publish --check-url` can resume without re-uploading identical files

This means the workflow is safe to keep enabled on every protected `main` push, but **a new PyPI
release still requires a version bump** in `pyproject.toml` and `src/g_sheet_mcp/__init__.py`.

### Optional alternative — trusted publishing

If you prefer not to store a PyPI token in GitHub, you can switch back to trusted publishing.

Configure a PyPI trusted publisher for:

- **Owner:** `mariadb-RupeshBiswas`
- **Repository:** `google-sheets-mcp`
- **Workflow:** `publish.yml`
- **Environment:** `pypi`

If GitHub Actions fails with `invalid-publisher` or `no corresponding publisher`, the PyPI trusted publisher does not yet match these workflow claims.

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
git tag vX.Y.Z
```

6. Push commits and tags:

```bash
git push origin main --tags
```

7. The GitHub `Publish` workflow will auto-run on protected `main`
8. If the workflow logs that the version already exists on PyPI, bump the version and push again

---

## Versioning strategy

This project uses **PEP 440-compliant Semantic Versioning**.

- **Patch** — backward-compatible fixes
- **Minor** — backward-compatible features and pre-1.0 breaking changes
- **Major** — reserved for `1.0.0` and later stable breaking changes

Canonical policy and examples → **[docs/VERSIONING.md](VERSIONING.md)**

---

## Using the published package

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

**Published package (PyPI):**

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

The project also supports GitHub and local-clone usage when you need unreleased changes or development workflows.
