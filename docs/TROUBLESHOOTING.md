# Troubleshooting

## Authentication errors

### `AuthError: No Application Default Credentials found`

**Cause:** The ADC file does not exist.

**Fix:**
```bash
gcloud auth login --enable-gdrive-access --update-adc
```

### `403 Access denied` / `PermissionError`

**Cause:** Your Google account does not have Viewer access to the spreadsheet.

**Fix:**
1. Open the spreadsheet in your browser
2. Click **Share** → add your Google account with Viewer access
3. Alternatively, ask the sheet owner to share it with you

### `403 insufficient permissions`

**Cause:** Old ADC file was created without the Drive scope (e.g. via plain `gcloud auth application-default login`).

**Fix:** Re-run with the correct flags:
```bash
gcloud auth login --enable-gdrive-access --update-adc
```

### `AuthError: Could not refresh credentials`

**Cause:** No network access, or the token has been revoked.

**Fix:**
```bash
gcloud auth revoke --all
gcloud auth login --enable-gdrive-access --update-adc
```

---

## Spreadsheet errors

### `404 Spreadsheet not found` / `FileNotFoundError`

**Causes:**
- Wrong spreadsheet ID in the URL
- Spreadsheet was deleted or moved
- You copied the wrong part of the URL

**Fix:** Double-check the URL. The ID is the long string between `/d/` and `/edit`:
```
https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
```

### `ValueError: Cannot extract a spreadsheet ID`

**Cause:** You passed something that is neither a valid Google Sheets URL nor a bare spreadsheet ID (min 20 alphanumeric characters).

**Fix:** Pass the full URL or just the ID string.

### `ValueError: sheet_title must be a non-empty string`

**Cause:** Empty string passed as the sheet tab name.

**Fix:** Use the exact tab name, e.g. `Sheet1` or `Example Sheet 1`.

### `LookupError: Sheet '...' not found`

**Cause:** The specified `sheet_title` does not match any tab in the spreadsheet (case-sensitive).

**Fix:** Call `list_sheets` first to see available tab names, then use the exact name.

### `RuntimeError: Google Sheets API rate limit exceeded`

**Cause:** Too many requests in a short period (429 from the API).

**Fix:** Wait 30–60 seconds and try again. If this happens frequently, add delays between batch calls.

---

## Editor / IDE issues

### Server not appearing in editor MCP panel

1. Verify `uv` is installed: `uv --version`
2. Verify the path in the config is the **absolute** path to this repo
3. Run `uv run g-sheet-mcp` manually in the terminal — if it errors, fix that first
4. Check the editor's developer console / logs for MCP errors

### Editor uses a different PATH than the terminal

Some editors launch processes without the full shell PATH.

**Fix:** Use the full absolute path to `uv`:
```bash
which uv   # e.g. /opt/homebrew/bin/uv
```

Then in the editor config:
```json
{
  "command": "/opt/homebrew/bin/uv",
  "args": ["--directory", "/absolute/path/to/google-sheets-mcp", "run", "g-sheet-mcp"]
}
```

### Works in terminal but not in editor

**Cause:** The editor-spawned process cannot find the ADC credentials because `HOME` or the user environment differs.

**Fix:** Explicitly set the credentials path in the editor MCP config:
```json
{
  "env": {
    "GOOGLE_APPLICATION_CREDENTIALS": "/Users/yourname/.config/gcloud/application_default_credentials.json"
  }
}
```

---

## Test failures

### Unit tests fail with import errors

```bash
uv sync --extra dev
uv run pytest tests/ -v --ignore=tests/test_integration.py
```

### Integration tests skipped

Integration tests require both `INTEGRATION=1` and `TEST_SPREADSHEET_ID`:
```bash
INTEGRATION=1 TEST_SPREADSHEET_ID=your_test_spreadsheet_id uv run pytest tests/test_integration.py -v -s
```

### Integration tests fail with auth errors

Ensure ADC is set up:
```bash
gcloud auth login --enable-gdrive-access --update-adc
INTEGRATION=1 TEST_SPREADSHEET_ID=your_test_spreadsheet_id uv run pytest tests/test_integration.py -v -s
```

---

## Debugging the server

### Enable debug logging

```bash
uv run g-sheet-mcp --debug
```

### Inspect tools with MCP Inspector

```bash
uv run mcp dev src/g_sheet_mcp/server.py
# → Open http://localhost:5173
```

### Test with curl (HTTP mode)

```bash
uv run g-sheet-mcp --http &

# List available tools
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | python3 -m json.tool
```

---

## Getting more help

1. Run `uv run g-sheet-mcp --debug` and capture the stderr output
2. Check if the same error occurs with the MCP Inspector
3. Confirm your `gcloud auth list` shows an active account
4. Open an issue with the full error message and reproduction steps
