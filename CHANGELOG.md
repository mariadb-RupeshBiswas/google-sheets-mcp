# Changelog

## [Unreleased]

### Added
- `read_sheet_as_records` tool: returns rows as `[{header: value}]` dicts — LLM-friendly format
- Auto-auth flow in `auth.py`: triggers `gcloud auth login` if no ADC file found
- `credentials_exist()` and `ensure_authenticated()` helpers in auth module
- `_gcloud_installed()` check with actionable error when gcloud is missing
- `_quote_sheet()` helper to safely wrap sheet names containing spaces or quotes
- `_validate_render_option()` helper to validate value_render_option parameter
- `_client_lock` threading.Lock in sheets.py for thread-safe SheetsClient init
- Double-checked locking in `_get_client()` in server.py
- Rate limit (429) and server error (5xx) cases in `_raise_friendly`
- `docs/QUICKSTART.md` — 5-minute setup guide
- `docs/AUTH.md` — authentication deep-dive
- `docs/EDITOR_SETUP.md` — step-by-step guides for Windsurf, Cursor, Claude Desktop, VS Code, Zed, Claude Code
- `docs/TROUBLESHOOTING.md` — common errors and fixes
- `agents/AGENT_INSTRUCTIONS.md` — tool usage guide for LLM agents
- `agents/SYSTEM_PROMPT.md` — copy-paste system prompt for agent configurations
- `agents/EXAMPLES.md` — real interaction examples with code
- `.cursor/rules` — Cursor IDE project rules
- `.windsurf/rules.md` — Windsurf IDE project rules
- `mcp-config-examples/` — ready-to-use config snippets per editor
- `LICENSE` — MIT license

### Changed
- `_raise_friendly` return type fixed to `-> NoReturn`
- `read_sheet` now uses `_quote_sheet()` for correct A1 range notation
- `get_cell` now uses `_quote_sheet()` and validates row/column >= 1
- Input validation added to `get_spreadsheet_info`, `read_range`, `read_sheet`, `get_cell`, `find_in_spreadsheet`, `batch_read_ranges`
- `find_in_spreadsheet` raises `LookupError` when `sheet_title` is not found in the spreadsheet
- `batch_read_ranges` raises `ValueError` when passed an empty list
- README rewritten with all editor integrations, new tool, docs links, project structure

### Tests
- `test_auth.py` expanded: TestCredentialsExist, TestEnsureAuthenticated, updated TestGetCredentials
- `test_sheets.py` expanded: TestQuoteSheet, TestValidateRenderOption, TestInputValidation, TestHttpErrorHandling, TestReadSheetAsRecords, TestFindInSpreadsheetUnknownSheet
- `test_integration.py` rewritten: 8 test classes covering all 8 tabs, all tools, batch, find, URL/ID acceptance
