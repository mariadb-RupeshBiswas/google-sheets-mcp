# Versioning Policy

This project uses **PEP 440-compliant Semantic Versioning** for public releases.

## Version format

Normal releases use:

```text
MAJOR.MINOR.PATCH
```

Examples:

- `0.1.0`
- `0.1.1`
- `1.0.0`

Optional pre-releases use the standard PEP 440 suffixes:

- `0.2.0a1` — alpha
- `0.2.0b1` — beta
- `0.2.0rc1` — release candidate

Avoid `.postN` for bug fixes or functional changes. Per Python packaging guidance, post-releases should be reserved for metadata-only corrections that do not change the shipped software.

## Standards behind this policy

This policy follows:

- **PEP 440** for valid Python package versions on PyPI
- **Semantic Versioning** for deciding which part of the version to increment

In short:

- **MAJOR** for incompatible public API changes
- **MINOR** for backward-compatible features
- **PATCH** for backward-compatible fixes

## What counts as the public API here

For this project, the public API includes:

- The package name: `g-sheet-mcp`
- The CLI entry point: `g-sheet-mcp`
- The MCP server identity: `google-sheets`
- The MCP tool names, parameters, and response shapes
- The documented resource URI: `spreadsheet://{spreadsheet_id}/info`
- The documented authentication flow and supported editor setup patterns

## Current pre-1.0 policy

The project is still in the `0.y.z` phase.

While the package remains below `1.0.0`, follow these rules:

- **PATCH** (`0.1.0` → `0.1.1`)
  - backward-compatible bug fixes
  - backward-compatible auth/reliability fixes
  - packaging metadata fixes that should ship in a new PyPI release
  - dependency updates that do not change the public API

- **MINOR** (`0.1.0` → `0.2.0`)
  - new MCP tools, resources, or backward-compatible features
  - new CLI flags or new user-visible capabilities
  - deprecations
  - intentionally breaking public API changes while still pre-1.0

- **MAJOR**
  - reserve `1.0.0` for the first stable release where the public API is considered committed

## Post-1.0 policy

Once the project reaches `1.0.0`, use strict SemVer:

- **MAJOR** for breaking changes
- **MINOR** for backward-compatible features and deprecations
- **PATCH** for backward-compatible fixes only

## When not to bump the version

Do **not** bump the package version for changes that are not intended to produce a new PyPI release, such as:

- docs-only changes
- CI-only changes
- GitHub settings/workflow changes that do not need a new published package
- repository maintenance that does not affect the shipped distribution

This repo’s publish workflow already skips cleanly when the current version is already fully published on PyPI, so non-release commits can still land on `main` without forcing a version bump.

## Release checklist

When cutting a new package release:

1. Choose the next version using the rules above
2. Update both:
   - `pyproject.toml`
   - `src/g_sheet_mcp/__init__.py`
3. Update `CHANGELOG.md`
4. Run release checks:
   - `uv run ruff check src tests`
   - `uv run mypy src`
   - `uv run pytest tests/ --ignore=tests/test_integration.py -q`
5. Build the package
6. Push to protected `main`
7. Let the `Publish` workflow publish the new version if it is not already on PyPI

## Practical examples

- **Fix ADC reload bug without breaking callers**
  - `0.1.0` → `0.1.1`

- **Add a new MCP tool**
  - `0.1.1` → `0.2.0`

- **Rename an existing tool or change a response shape incompatibly while still pre-1.0**
  - `0.2.0` → `0.3.0`

- **Declare the public API stable**
  - `0.3.0` → `1.0.0`
