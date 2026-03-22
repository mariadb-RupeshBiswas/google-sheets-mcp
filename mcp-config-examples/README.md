# 🧩 MCP Config Examples

Ready-to-use configuration snippets for connecting the Google Sheets MCP server to various editors and AI assistants.

These JSON files are the **local clone** variants. GitHub and PyPI / `uvx` variants are documented in [docs/EDITOR_SETUP.md](../docs/EDITOR_SETUP.md).

## Usage

1. Copy the config file for your editor
2. Replace `/absolute/path/to/google-sheets-mcp` with the real path on your machine
3. Paste into your editor's MCP configuration file

---

## Windsurf

**Config file:** `~/.codeium/windsurf/mcp_config.json`

```bash
cp windsurf.json ~/.codeium/windsurf/mcp_config.json
# Edit the path, then restart Windsurf
```

---

## Cursor

**Config file:** `~/.cursor/mcp.json`

```bash
cp cursor.json ~/.cursor/mcp.json
# Edit the path, then restart Cursor
```

---

## Claude Desktop

**Config file (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`

```bash
cp claude-desktop.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Edit the path, then restart Claude Desktop
```

---

## VS Code + GitHub Copilot

**Config file:** `~/.vscode/mcp.json`

```bash
cp vscode.json ~/.vscode/mcp.json
# Edit the path, then restart VS Code
```

---

## Zed

**Config file:** `~/.config/zed/settings.json`

Merge the contents of `zed.json` into your existing Zed settings.json.

---

## Claude Code (CLI)

```bash
claude mcp add --transport stdio google-sheets -- \
  uv --directory /absolute/path/to/google-sheets-mcp run g-sheet-mcp
```
