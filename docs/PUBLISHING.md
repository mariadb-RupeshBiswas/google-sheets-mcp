# Publishing to PyPI (Optional)

Publishing to PyPI enables simpler installation via `pip` or `uvx`. However, **this is completely optional** — the project works perfectly fine from a local clone or git URL.

---

## Before Publishing

### 1. Update project metadata

Edit `pyproject.toml`:

```toml
[project]
name = "g-sheet-mcp"
version = "0.1.0"  # Increment for each release

[project.urls]
Homepage = "https://github.com/yourusername/g_sheet_mcp"  # Update username
"Bug Tracker" = "https://github.com/yourusername/g_sheet_mcp/issues"
```

### 2. Verify package builds

```bash
uv build
# Creates dist/g_sheet_mcp-0.1.0.tar.gz and dist/g_sheet_mcp-0.1.0-py3-none-any.whl
```

### 3. Test the built package

```bash
# Install from local wheel
pip install dist/g_sheet_mcp-0.1.0-py3-none-any.whl

# Test it works
g-sheet-mcp --help
```

---

## Publishing to PyPI

### First-time setup

```bash
# Install twine
pip install twine

# Create PyPI account at https://pypi.org/account/register/
# Generate API token at https://pypi.org/manage/account/token/
```

### Configure credentials

```bash
# Create/edit ~/.pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

### Upload to PyPI

```bash
# Build fresh
uv build

# Upload to PyPI
twine upload dist/*
```

### Test installation

```bash
# In a fresh environment
pip install g-sheet-mcp

# Or with uvx
uvx g-sheet-mcp --help
```

---

## Alternative: Publish to TestPyPI First

Test the full workflow without polluting the real PyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ g-sheet-mcp
```

---

## Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **0.1.0** — Initial release
- **0.1.1** — Bug fixes
- **0.2.0** — New features (backward compatible)
- **1.0.0** — Stable API

Update `version` in `pyproject.toml` and `src/g_sheet_mcp/__init__.py`.

---

## GitHub Release Workflow

1. Update `CHANGELOG.md` with release notes
2. Commit version bump: `git commit -m "chore: bump version to 0.1.0"`
3. Tag the release: `git tag v0.1.0`
4. Push with tags: `git push origin main --tags`
5. Build and upload to PyPI (see above)
6. Create GitHub release from the tag

---

## Automation with GitHub Actions (Optional)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

Add `PYPI_API_TOKEN` to GitHub repo secrets.

---

## Usage After Publishing

### Simple installation

```bash
# With pip
pip install g-sheet-mcp

# With uvx (ephemeral)
uvx g-sheet-mcp

# With pipx (persistent)
pipx install g-sheet-mcp
```

### Editor configs become simpler

**Before (local):**
```json
{
  "command": "uv",
  "args": ["run", "--directory", "/path/to/g_sheet_mcp", "g-sheet-mcp"]
}
```

**After (published):**
```json
{
  "command": "g-sheet-mcp"
}
```

---

## Do You Need to Publish?

**No, if:**
- You're the only user
- You prefer local development workflow
- You want to avoid PyPI maintenance

**Yes, if:**
- You want others to easily install it
- You want simpler editor integration
- You want to share it with the community

The project is fully functional either way!
