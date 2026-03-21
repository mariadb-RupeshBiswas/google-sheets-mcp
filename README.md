# g-sheet-mcp

A **read-only** [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives
AI assistants (Claude, Cursor, Copilot, etc.) direct access to Google Sheets data — authenticated
via [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials).

No service account JSON.  No hardcoded secrets.  One command to authenticate, works everywhere.

---

## Features

| MCP Tool | Description |
|---|---|
| `get_spreadsheet_info` | Title, locale, timezone, and all sheet tab metadata |
| `list_sheets` | List every worksheet tab with row/column dimensions |
| `read_range` | Read an A1-notation range (e.g. `'Sheet1'!A1:D10`) |
| `read_sheet` | Read an entire worksheet by tab name (spaces in name handled automatically) |
| `read_sheet_as_records` | **Best for LLMs** — returns rows as `[{"col": val, ...}]` dicts |
| `get_cell` | Read a single cell by 1-based row/column index |
| `find_in_spreadsheet` | Substring search across all cells (with optional sheet filter) |
| `batch_read_ranges` | Read multiple ranges in one API call |

Both **full Google Sheets URLs** and **bare spreadsheet IDs** are accepted by all tools.  
Sheet names with **spaces** (e.g. `Example Sheet 1`) are quoted automatically.

---

## Installation

### Prerequisites

```bash
# Python 3.11+ and uv
brew install uv                  # macOS
# or: curl -LsSf https://astral.sh/uv/install.sh | sh

# Google Cloud SDK
brew install google-cloud-sdk
# or: https://cloud.google.com/sdk/docs/install
```

### Option 1: Local Clone (Recommended for Development)

```bash
git clone https://github.com/yourusername/g_sheet_mcp.git
cd g_sheet_mcp
uv sync
```

### Option 2: Run with uvx (No Installation Required)

```bash
# From GitHub (no clone needed)
uvx --from git+https://github.com/yourusername/g_sheet_mcp g-sheet-mcp

# From local path
uvx --from /absolute/path/to/g_sheet_mcp g-sheet-mcp
```

### Option 3: Install from PyPI (After Publishing)

```bash
# With pipx (persistent)
pipx install g-sheet-mcp

# Or just use uvx (ephemeral)
uvx g-sheet-mcp
```

See **[docs/PUBLISHING.md](docs/PUBLISHING.md)** for PyPI publishing guide (optional).

### 3. Authenticate (once)

```bash
gcloud auth login --enable-gdrive-access --update-adc
```

This writes `~/.config/gcloud/application_default_credentials.json`.  The server picks it up
automatically on every subsequent run — including auto-detection if it is missing.

### 4. Run the server

```bash
uv run g-sheet-mcp          # stdio mode (for MCP clients)
uv run g-sheet-mcp --http   # HTTP mode → http://127.0.0.1:8000/mcp
uv run g-sheet-mcp --debug  # verbose logging
```

---

## Documentation

- **[Quick Start](docs/QUICKSTART.md)** — 5-minute setup
- **[Editor Setup](docs/EDITOR_SETUP.md)** — Windsurf, Cursor, Claude Desktop, VS Code, Zed, Claude Code
- **[Authentication](docs/AUTH.md)** — ADC setup and troubleshooting
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** — Common issues and fixes
- **[Publishing](docs/PUBLISHING.md)** — PyPI publishing guide (optional)
- **[Contributing](CONTRIBUTING.md)** — Development guide

---

## Editor Integration

> Full step-by-step guides → **[docs/EDITOR_SETUP.md](docs/EDITOR_SETUP.md)**

Quick JSON snippets for each editor — replace `/absolute/path/to/g_sheet_mcp`:

### Windsurf — `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/g_sheet_mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

### Cursor — `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/g_sheet_mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

### Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/g_sheet_mcp", "g-sheet-mcp"]
    }
  }
}
```

### VS Code + GitHub Copilot — `~/.vscode/mcp.json`

```json
{
  "servers": {
    "google-sheets": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/g_sheet_mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

### Zed — `~/.config/zed/settings.json`

```json
{
  "context_servers": {
    "google-sheets": {
      "command": {
        "path": "uv",
        "args": ["--directory", "/absolute/path/to/g_sheet_mcp", "run", "g-sheet-mcp"]
      }
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add --transport stdio google-sheets -- \
  uv run --directory /absolute/path/to/g_sheet_mcp g-sheet-mcp
```

---

## Example Prompts

Once connected to any editor:

```
List all sheet tabs in https://docs.google.com/spreadsheets/d/YOUR_ID/edit
```

```
Read 'Example Sheet 1' from that spreadsheet as records and show me the first 5 rows
```

```
Find all cells containing "invoice" in the spreadsheet
```

```
Read columns A through D from every tab in that spreadsheet
```

---

## Available MCP Tools — Reference

### `get_spreadsheet_info`
```
spreadsheet_id_or_url: str       # Full URL or bare spreadsheet ID
→ { spreadsheet_id, title, locale, time_zone, sheets: [SheetProperties, ...] }
```

### `list_sheets`
```
spreadsheet_id_or_url: str
→ [{ sheet_id, title, index, sheet_type, row_count, column_count }, ...]
```

### `read_range`
```
spreadsheet_id_or_url: str
range_notation: str              # e.g. "'Sheet1'!A1:D10" or "A1:D10"
value_render_option: str         # FORMATTED_VALUE* | UNFORMATTED_VALUE | FORMULA
→ { sheet_title, range_notation, row_count, column_count, values: [[...], ...] }
```

### `read_sheet`
```
spreadsheet_id_or_url: str
sheet_title: str                 # Exact tab name (spaces OK — quoted automatically)
value_render_option: str
→ same as read_range
```

### `read_sheet_as_records`  ★ LLM-friendly
```
spreadsheet_id_or_url: str
sheet_title: str                 # First row is used as column headers
value_render_option: str
max_rows: int                    # Safety cap, default 1000
→ [{"col_a": val, "col_b": val, ...}, ...]  — missing cells → null
```

### `get_cell`
```
spreadsheet_id_or_url: str
sheet_title: str
row: int                         # 1-based row (row 1 = first row)
column: int                      # 1-based column (1=A, 2=B, ...)
value_render_option: str
→ { row, column, a1_notation, value }
```

### `find_in_spreadsheet`
```
spreadsheet_id_or_url: str
query: str                       # Non-empty search string
sheet_title: str                 # "" = search all sheets
case_sensitive: bool             # default False
max_results: int                 # default 50, capped at 500
→ [{ sheet_title, row, column, a1_notation, matched_value }, ...]
```

### `batch_read_ranges`
```
spreadsheet_id_or_url: str
ranges: list[str]                # e.g. ["'Sheet1'!A1:B5", "'Sheet2'!C1:C10"]
value_render_option: str
→ [RangeData, ...]               — same order as input ranges
```

---

## Development

```bash
uv sync --extra dev              # install with dev deps

uv run pytest                    # unit tests (38+ cases)
INTEGRATION=1 uv run pytest tests/test_integration.py -v -s   # live API tests

uv run ruff check src tests      # lint
uv run mypy src                  # type check

uv run mcp dev src/g_sheet_mcp/server.py   # MCP Inspector (interactive)
```

---

## Authentication

```
gcloud auth login --enable-gdrive-access --update-adc
→ ~/.config/gcloud/application_default_credentials.json
```

**Required scopes** (set automatically by `--enable-gdrive-access`):
- `spreadsheets.readonly`
- `drive.readonly`

The server auto-detects missing credentials and triggers the browser auth flow.  
Full details → **[docs/AUTH.md](docs/AUTH.md)**

---

## Project structure

```
g_sheet_mcp/
├── src/g_sheet_mcp/
│   ├── auth.py        # ADC credential loading + auto-auth flow
│   ├── models.py      # Pydantic models for all API responses
│   ├── sheets.py      # Google Sheets API v4 wrapper (SheetsClient)
│   └── server.py      # FastMCP server — 8 tools + 1 resource
├── tests/
│   ├── conftest.py         # Shared fixtures + mock API responses
│   ├── test_auth.py        # Auth unit tests
│   ├── test_sheets.py      # Sheets client unit tests
│   ├── test_server.py      # MCP tool unit tests
│   └── test_integration.py # Live API tests (INTEGRATION=1)
├── docs/
│   ├── QUICKSTART.md       # 5-minute setup guide
│   ├── EDITOR_SETUP.md     # Per-editor integration (Windsurf, Cursor, VS Code, Zed…)
│   ├── AUTH.md             # Authentication deep-dive
│   └── TROUBLESHOOTING.md  # Common errors and fixes
├── mcp-config-examples/    # Ready-to-use config files per editor
├── agents/                 # LLM instruction files
└── pyproject.toml
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `AuthError: No Application Default Credentials found` | Run `gcloud auth login --enable-gdrive-access --update-adc` |
| `PermissionError: Access denied` | Share the spreadsheet with your Google account (Viewer) |
| `FileNotFoundError: Spreadsheet not found` | Check the spreadsheet ID/URL |
| `403 insufficient permissions` | Re-run `gcloud auth login` — old ADC may lack Drive scope |
| `RuntimeError: rate limit exceeded` | Wait 30s and retry |
| `LookupError: Sheet '...' not found` | Call `list_sheets` first to see exact tab names |

Full guide → **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**

---

## License

MIT — see [LICENSE](LICENSE)
