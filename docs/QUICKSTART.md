# Quick Start — 5 minutes to first data

## Prerequisites

| Tool | Install |
|---|---|
| Python 3.11+ | `brew install python` or [python.org](https://python.org) |
| uv | `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Google Cloud SDK | `brew install google-cloud-sdk` or [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install) |

---

## Step 1 — Clone and install

```bash
git clone <your-repo-url>
cd g_sheet_mcp
uv sync
```

---

## Step 2 — Authenticate (once)

```bash
gcloud auth login --enable-gdrive-access --update-adc
```

A browser window opens. Sign in with the Google account that has access to your spreadsheets.

> **What this does:** Writes `~/.config/gcloud/application_default_credentials.json` with
> Drive + Sheets scopes. The server auto-detects and uses this file on every run — no extra
> configuration needed.

---

## Step 3 — Test it works

```bash
INTEGRATION=1 TEST_SPREADSHEET_ID=your_id uv run pytest tests/test_integration.py -v -s
```

You should see the spreadsheet title and all sheet tabs printed in the output.

---

## Step 4 — Connect to your editor

Pick your editor from the table below and follow the link:

| Editor | Guide |
|---|---|
| **Windsurf** | [EDITOR_SETUP.md → Windsurf](EDITOR_SETUP.md#windsurf) |
| **Cursor** | [EDITOR_SETUP.md → Cursor](EDITOR_SETUP.md#cursor) |
| **Claude Desktop** | [EDITOR_SETUP.md → Claude Desktop](EDITOR_SETUP.md#claude-desktop) |
| **VS Code + Copilot** | [EDITOR_SETUP.md → VS Code](EDITOR_SETUP.md#vs-code--github-copilot) |
| **Zed** | [EDITOR_SETUP.md → Zed](EDITOR_SETUP.md#zed) |
| **Claude Code (CLI)** | [EDITOR_SETUP.md → Claude Code](EDITOR_SETUP.md#claude-code-cli) |

---

## Step 5 — Ask your AI a question

Once connected, try prompts like:

```
Read all sheet tabs from https://docs.google.com/spreadsheets/d/YOUR_ID/edit
```

```
Show me the first 10 rows of 'Sheet1' as a table
```

```
Find all cells containing "invoice" in this spreadsheet: YOUR_SPREADSHEET_URL
```

---

## What's next?

- Full tool reference → [README.md](../README.md#available-mcp-tools--reference)
- Authentication details → [AUTH.md](AUTH.md)
- Troubleshooting → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
