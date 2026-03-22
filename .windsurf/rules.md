# Windsurf Rules — g-sheet-mcp

This is a read-only Google Sheets MCP server using FastMCP + Google Sheets API v4 + ADC.

## Stack
- Python 3.11, uv, FastMCP (mcp[cli]>=1.9.0), google-api-python-client, pydantic v2

## Key files
- src/g_sheet_mcp/auth.py    — ADC loading + auto-auth flow (ensure_authenticated)
- src/g_sheet_mcp/sheets.py  — SheetsClient (all API calls, _quote_sheet, validation)
- src/g_sheet_mcp/models.py  — Pydantic response models
- src/g_sheet_mcp/server.py  — FastMCP server with 8 tools, 1 resource, thread-safe client init, and ADC-aware client reload

## Development rules
- Always use `from __future__ import annotations`
- Run: `uv run`, Install: `uv sync`, Lock: `uv lock`
- Never hardcode credentials; ADC only
- Keep docs/tests/examples sanitized; never commit real spreadsheet IDs, emails, or customer/internal data
- In user-facing setup docs and editor configuration examples, recommend the published PyPI flow `uvx g-sheet-mcp` first; keep GitHub and local-clone flows as alternatives for unreleased changes or repository development
- Follow `docs/VERSIONING.md` for release numbering; use PEP 440-compliant SemVer
- Keep `pyproject.toml` and `src/g_sheet_mcp/__init__.py` in sync when cutting a package release
- Do not bump the package version for docs-only or CI-only changes unless a new PyPI release is intended
- All public methods require docstrings
- Input validation: ValueError for empty strings, out-of-range ints
- Sheet names with spaces: use _quote_sheet() in range notation (auto-applied by read_sheet)
- Thread safety: use _client_lock (double-checked locking) for SheetsClient init
- Tests: `uv run pytest` (unit) or `INTEGRATION=1 uv run pytest tests/test_integration.py`

## MCP capabilities
get_spreadsheet_info, list_sheets, read_range, read_sheet, read_sheet_as_records,
get_cell, find_in_spreadsheet, batch_read_ranges, spreadsheet://{spreadsheet_id}/info

## Auth
gcloud auth login --enable-gdrive-access --update-adc
→ ~/.config/gcloud/application_default_credentials.json

If ADC is refreshed while the server is already running, retry the request once before restarting the editor — the server reloads updated ADC on the next call.

## Testing
Unit tests: uv run pytest tests/ --ignore=tests/test_integration.py
Integration tests: INTEGRATION=1 TEST_SPREADSHEET_ID=your_test_spreadsheet_id uv run pytest tests/test_integration.py
