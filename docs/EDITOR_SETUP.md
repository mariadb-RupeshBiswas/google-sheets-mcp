# 🧩 Editor Integration Guide

Connect the Google Sheets MCP server to your AI coding assistant.

**Prerequisites:** Complete [QUICKSTART.md](QUICKSTART.md) steps 1–2 first (install + authenticate).

---

## Recommended default

For most users, use the published PyPI package with `uvx g-sheet-mcp`.
Use the GitHub or local-clone variants only if you need unreleased changes or are developing the repository itself.

If you need reproducible editor setup, pin an exact release:

```bash
uvx --from g-sheet-mcp==0.1.2 g-sheet-mcp
```

---

## Windsurf

Windsurf reads MCP config from `~/.codeium/windsurf/mcp_config.json`.

### Step 1 — Open MCP settings

`Windsurf menu → Settings → MCP` (or edit the file directly).

### Step 2 — Add the server

**Option A: From PyPI (recommended)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["g-sheet-mcp"]
    }
  }
}
```

If you want to pin a specific release for reproducibility, use:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["--from", "g-sheet-mcp==0.1.2", "g-sheet-mcp"]
    }
  }
}
```

**Option B: From GitHub (no path needed)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp", "g-sheet-mcp"]
    }
  }
}
```

**Option C: Local clone (requires full path)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/google-sheets-mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

Replace `/absolute/path/to/google-sheets-mcp` with your actual path.

### Step 3 — Restart Windsurf

Close and reopen Windsurf. In Cascade, type:

```
What sheets are in https://docs.google.com/spreadsheets/d/YOUR_ID/edit?
```

---

## Cursor

Cursor reads MCP config from `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project).

### Step 1 — Open MCP settings

`Cursor menu → Settings → Cursor Settings → MCP` and click **Add new global MCP server**,
or edit `~/.cursor/mcp.json` directly.

### Step 2 — Add the server

**Option A: From PyPI (recommended)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["g-sheet-mcp"]
    }
  }
}
```

**Option B: From GitHub (no path needed)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp", "g-sheet-mcp"]
    }
  }
}
```

**Option C: Local clone**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/google-sheets-mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

### Step 3 — Restart Cursor

After saving, restart Cursor. A green dot next to **google-sheets** in the MCP panel
confirms the server is running.

### Step 4 — Verify

Open a Composer chat and type:

```
Use the google-sheets MCP to list the sheets in: YOUR_SPREADSHEET_URL
```

---

## Claude Desktop

Claude Desktop reads config from:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### Step 1 — Edit config

Open the config file (create it if missing) and add:

**Option A: From PyPI (recommended)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["g-sheet-mcp"]
    }
  }
}
```

**Option B: From GitHub (no path needed)**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp", "g-sheet-mcp"]
    }
  }
}
```

**Option C: Local clone**

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/google-sheets-mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

### Step 2 — Restart Claude Desktop

Fully quit and reopen Claude Desktop. A hammer icon in the chat input bar shows
that MCP tools are available.

### Step 3 — Test

Ask Claude:

> *"Read the first sheet from https://docs.google.com/spreadsheets/d/YOUR_ID/edit"*

---

## VS Code + GitHub Copilot

VS Code supports MCP via the Copilot Chat extension (VS Code 1.99+).

### Step 1 — Open MCP config

`Ctrl/Cmd+Shift+P` → **"MCP: Open User Configuration"**

Or edit `~/.vscode/mcp.json` directly.

### Step 2 — Add the server

**Option A: From PyPI (recommended)**

```json
{
  "servers": {
    "google-sheets": {
      "type": "stdio",
      "command": "uvx",
      "args": ["g-sheet-mcp"]
    }
  }
}
```

**Option B: From GitHub (no path needed)**

```json
{
  "servers": {
    "google-sheets": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp", "g-sheet-mcp"]
    }
  }
}
```

**Option C: Local clone**

```json
{
  "servers": {
    "google-sheets": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/google-sheets-mcp", "run", "g-sheet-mcp"]
    }
  }
}
```

### Step 3 — Enable in Copilot Chat

Open Copilot Chat, switch to **Agent mode** (the `@` dropdown), and verify
`google-sheets` appears in the tools list.

### Step 4 — Test

```
@workspace Use google-sheets to read Sheet1 from YOUR_SPREADSHEET_URL
```

---

## Zed

Zed supports MCP in its Assistant panel.

### Step 1 — Edit Zed settings

`Zed → Settings → Open Settings (JSON)` or `~/.config/zed/settings.json`.

### Step 2 — Add the server

**Option A: From PyPI (recommended)**

```json
{
  "context_servers": {
    "google-sheets": {
      "command": {
        "path": "uvx",
        "args": ["g-sheet-mcp"]
      }
    }
  }
}
```

**Option B: From GitHub (no path needed)**

```json
{
  "context_servers": {
    "google-sheets": {
      "command": {
        "path": "uvx",
        "args": [
          "--from",
          "git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp",
          "g-sheet-mcp"
        ]
      }
    }
  }
}
```

**Option C: Local clone**

```json
{
  "context_servers": {
    "google-sheets": {
      "command": {
        "path": "uv",
        "args": [
          "--directory",
          "/absolute/path/to/google-sheets-mcp",
          "run",
          "g-sheet-mcp"
        ]
      }
    }
  }
}
```

### Step 3 — Restart Zed

Reopen Zed and open the Assistant panel. The server will appear in the context list.

---

## Claude Code (CLI)

Claude Code is Anthropic's terminal-based coding agent.

**Option A: From PyPI (recommended)**

```bash
claude mcp add --transport stdio google-sheets -- \
  uvx g-sheet-mcp
```

**Option B: From GitHub (no path needed)**

```bash
claude mcp add --transport stdio google-sheets -- \
  uvx --from git+https://github.com/mariadb-RupeshBiswas/google-sheets-mcp g-sheet-mcp
```

**Option C: Local clone**

```bash
claude mcp add --transport stdio google-sheets -- \
  uv --directory /absolute/path/to/google-sheets-mcp run g-sheet-mcp
```

Verify:

```bash
claude mcp list
```

Use in a session:

```bash
claude
> Read all tabs from https://docs.google.com/spreadsheets/d/YOUR_ID/edit
```

---

## MCP Inspector (debugging)

Inspect and test tools interactively without an editor:

```bash
uv run mcp dev src/g_sheet_mcp/server.py
```

Opens a local web UI at `http://localhost:5173` where you can call any tool manually.

---

## HTTP mode (curl / custom clients)

Run the server in HTTP mode for programmatic access:

```bash
uvx g-sheet-mcp --http
# → Listening on http://127.0.0.1:8000/mcp
```

If you are testing a local checkout instead, run `uv run g-sheet-mcp --http` from the repo.

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/list","params":{}}'
```

---

## Troubleshooting integrations

| Symptom | Fix |
|---|---|
| Server not listed in editor | Check the command in the config; for the recommended setup run `which uvx` to confirm `uvx` is on PATH |
| Green dot → red after start | Check editor developer console; run the same command as your config manually — for the recommended setup, try `uvx g-sheet-mcp` |
| `AuthError` on first call | Run `gcloud auth login --enable-gdrive-access --update-adc`, then retry the request — restart is usually not required |
| Works in terminal, not editor | Editor may use a different PATH — use the full path to `uvx` (or `uv` for a local-clone config) |

Full troubleshooting → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
