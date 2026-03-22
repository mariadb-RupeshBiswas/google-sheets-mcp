# 🤖 Google Sheets MCP — Agent Instructions

This file provides instructions for LLM agents using the `google-sheets` MCP server.

---

## Server identity

- **MCP server name:** `google-sheets`
- **Purpose:** Read-only access to Google Sheets via the Google Sheets API v4
- **Authentication:** Application Default Credentials (ADC) — no credentials needed from the agent
- **Access level:** Read-only; no writes, no deletes
- **Public examples:** Use only sanitized, generic examples unless the user provides real data explicitly

---

## Available capabilities (8 tools + 1 resource)

| Tool | When to use |
|---|---|
| `get_spreadsheet_info` | First call — discover title, locale, and all tab names |
| `list_sheets` | List all worksheet tabs with row/column counts |
| `read_sheet_as_records` | **Preferred** — get data as named dicts; easiest to reason about |
| `read_sheet` | Get raw 2-D array for an entire tab |
| `read_range` | Read a specific A1 range (e.g. `'Sheet1'!A1:D10`) |
| `get_cell` | Read one cell by row/column number |
| `find_in_spreadsheet` | Search for text across all or one tab |
| `batch_read_ranges` | Fetch multiple ranges in one API call (efficient) |
| `spreadsheet://{spreadsheet_id}/info` | Read a plain-text metadata summary when the MCP client supports templated resources |

---

## Resource guidance

- **Resource URI template:** `spreadsheet://<spreadsheet_id>/info`
- **Best use case:** Quick title / locale / sheet-tab summary without a full tool call sequence
- **Fallback:** If the client does not surface templated resources, call `get_spreadsheet_info` instead

---

## Decision tree — which tool to call first

```
User mentions a spreadsheet URL or ID
    ↓
call get_spreadsheet_info(spreadsheet_id_or_url)
    → learn the title and all tab names
    ↓
User wants all data from a specific tab?
    → call read_sheet_as_records(url, sheet_title)   ← preferred
    → returns [{header: value, ...}, ...]
    
User wants specific columns/rows?
    → call read_range(url, "'Tab Name'!A1:D20")
    
User wants to search for something?
    → call find_in_spreadsheet(url, query)
    
User wants data from multiple tabs at once?
    → call batch_read_ranges(url, ["'Tab1'!A:Z", "'Tab2'!A:Z"])
```

---

## Input rules

### Spreadsheet ID or URL

All tools accept either format — always prefer the full URL when the user provides it:

```python
# Both are valid:
"https://docs.google.com/spreadsheets/d/1ABC.../edit"
"1ABC..."   # bare ID (20+ alphanumeric chars)
```

### Sheet titles with spaces

Sheet names with spaces MUST be wrapped in single quotes in range notation:

```python
# Correct:
"'Example Sheet 1'!A1:D10"
"'My Budget Sheet'!A:Z"

# Wrong (will fail for names with spaces):
"Example Sheet 1!A1:D10"
```

When using `read_sheet`, `read_sheet_as_records`, or `get_cell`, pass the title
**without** quotes — the server wraps them automatically.

### value_render_option

- `FORMATTED_VALUE` (default) — use this for display values (e.g. `"$1,234.56"`)
- `UNFORMATTED_VALUE` — use for raw numbers (e.g. `1234.56`)
- `FORMULA` — use when you need the formula text (e.g. `"=SUM(A1:A10)"`)

---

## Output formats

### `read_sheet_as_records` (best for LLMs)

```json
[
  {"id": "001", "name": "Item A", "category": "TypeX", "value": "100"},
  {"id": "002", "name": "Item B", "category": "TypeY", "value": "200"}
]
```

Missing cells in a row are returned as `null`.

### `read_sheet` / `read_range` (raw grid)

```json
{
  "sheet_title": "Sheet1",
  "range_notation": "'Sheet1'!A1:D3",
  "row_count": 3,
  "column_count": 4,
  "values": [
    ["id", "name", "category", "value"],
    ["001", "Item A", "TypeX", "100"],
    ["002", "Item B", "TypeY", "200"]
  ]
}
```

The first row is typically the header. Rows shorter than the max column count
simply omit trailing empty cells.

### `find_in_spreadsheet`

```json
[
  {
    "sheet_title": "Sheet1",
    "row": 1,
    "column": 1,
    "a1_notation": "A1",
    "matched_value": "id"
  }
]
```

---

## Error handling guidance

| Error type | Meaning | What to tell user |
|---|---|---|
| `AuthError` | Missing, expired, or revoked ADC credentials | "Run: `gcloud auth login --enable-gdrive-access --update-adc`, then retry the request" |
| `PermissionError` | No access to spreadsheet | "Make sure your Google account has Viewer access" |
| `FileNotFoundError` | Wrong spreadsheet ID | "Check the URL — the ID may be wrong" |
| `LookupError: Sheet not found` | Wrong tab name | Call `list_sheets` to show available tab names |
| `ValueError: row must be >= 1` | Invalid row/column | Rows and columns are 1-based, not 0-based |
| `RuntimeError: rate limit` | Too many requests | Wait 30 seconds and retry |

If the user has just re-run `gcloud auth login --enable-gdrive-access --update-adc`, retry the
tool call once before asking them to restart the editor. The server reloads updated ADC on the
next request.

---

## Efficiency tips

1. **Call `get_spreadsheet_info` once** and cache the tab names — avoid calling it on every operation
2. **Use `batch_read_ranges`** when you need data from multiple tabs simultaneously
3. **Use `read_sheet_as_records`** instead of `read_sheet` when you need to reason about column values — it's much easier to work with named dicts than 2-D arrays
4. **Use `find_in_spreadsheet` with `sheet_title`** to scope searches when you know which tab to look in — it avoids scanning all tabs
5. **Set `max_rows`** on `read_sheet_as_records` if you only need a sample of data

---

## Example agent workflow

```
User: "Show me the first 5 rows from Sheet1"

Agent:
1. call read_sheet_as_records(
     "https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit",
     "Sheet1",
     max_rows=5
   )
2. Present the result as a formatted table
```

## Repo maintenance note

If you are modifying this repository itself rather than only using the MCP tools:
- follow `docs/VERSIONING.md` for release numbering
- keep `pyproject.toml` and `src/g_sheet_mcp/__init__.py` in sync when preparing a new package release
- recommend the published PyPI setup `uvx g-sheet-mcp` first in user-facing setup docs and editor configuration guidance
- mention GitHub and local-clone setup only as alternatives for unreleased changes or repository development
