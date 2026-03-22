# 🧩 MCP Config Examples

Ready-to-use configuration snippets for connecting the Google Sheets MCP server to various editors and AI assistants.

These JSON files now use the recommended published PyPI / `uvx` setup.
GitHub and local-clone variants are documented in [docs/EDITOR_SETUP.md](../docs/EDITOR_SETUP.md).

## Usage

1. Copy the config file for your editor
2. Paste it into your editor's MCP configuration file
3. Restart the editor so it reloads MCP servers

---

## Windsurf

**Config file:** `~/.codeium/windsurf/mcp_config.json`

```bash
cp windsurf.json ~/.codeium/windsurf/mcp_config.json
# Restart Windsurf
```

---

## Cursor

**Config file:** `~/.cursor/mcp.json`

```bash
cp cursor.json ~/.cursor/mcp.json
# Restart Cursor
```

---

## Claude Desktop

**Config file (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`

```bash
cp claude-desktop.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Restart Claude Desktop
```

---

## VS Code + GitHub Copilot

**Config file:** `~/.vscode/mcp.json`

```bash
cp vscode.json ~/.vscode/mcp.json
# Restart VS Code
```

---

## Zed

**Config file:** `~/.config/zed/settings.json`

Merge the contents of `zed.json` into your existing Zed settings.json and restart Zed.

---

## Claude Code (CLI)

```bash
claude mcp add --transport stdio google-sheets -- \
  uvx g-sheet-mcp
```
