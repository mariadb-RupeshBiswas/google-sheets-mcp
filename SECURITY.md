# Security Policy

## Security Model

This project is a **read-only** MCP server with the following security guarantees:

### ✅ Safe by design

1. **Read-only API access** — Requests only `*.readonly` scopes; no write/delete operations possible
2. **No credentials stored** — Uses Application Default Credentials (ADC) managed by Google Cloud SDK
3. **No hardcoded secrets** — All authentication via user's own Google account
4. **Input validation** — All user inputs are validated; empty strings, out-of-range values, and invalid enums are rejected
5. **Thread-safe** — Double-checked locking for shared resources
6. **Sandboxed execution** — Runs as a local process under the user's own OS account

### 🔐 Authentication & Authorization

- **ADC-based** — Uses `gcloud auth login --enable-gdrive-access --update-adc`
- **Scope-limited** — Only requests `spreadsheets.readonly` and `drive.readonly`
- **Share-aware** — Respects Google Sheets sharing settings; user must have Viewer access
- **Token refresh** — Credentials auto-refresh; no manual token management

### 🛡️ Attack surface

| Risk | Mitigation |
|---|---|
| Credential theft | ADC file is stored by `gcloud` SDK with OS-level permissions; never transmitted by this server |
| Code injection | All inputs are validated; no `eval()` or dynamic code execution |
| Path traversal | All file operations use fixed paths or ADC environment variables |
| SSRF | Only connects to `sheets.googleapis.com` (Google's official API endpoint) |
| Dependency vulnerabilities | Pins major versions; `uv.lock` ensures reproducible builds |

## Reporting a Vulnerability

If you discover a security vulnerability, please email the maintainer or open a **private** security advisory on GitHub.

**Do NOT** open a public issue for security vulnerabilities.

We will respond within 48 hours and work with you to address the issue.

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x (current) | ✅ |

## Security Best Practices for Users

1. **Never share your ADC credentials** — Treat `~/.config/gcloud/application_default_credentials.json` as a secret
2. **Revoke access when done** — Run `gcloud auth revoke` if you no longer need the server
3. **Use service accounts in CI/CD** — For automated environments, use a dedicated service account with minimal permissions
4. **Review spreadsheet sharing** — Only share spreadsheets with accounts that need access
5. **Monitor API usage** — Check your Google Cloud Console for unexpected API calls

## Dependencies

All dependencies are from trusted sources:
- `google-api-python-client` — Official Google client library
- `google-auth` — Official Google auth library
- `fastmcp` — Official MCP SDK from Anthropic
- `pydantic` — Industry-standard data validation library

Dependency versions are pinned in `pyproject.toml` and locked in `uv.lock`.

## Audit Log

- **2025-01-XX** — Initial security review completed; no issues found
- Input validation added to all public methods
- Thread safety implemented for shared client
- `.gitignore` configured to block credentials
- Security policy documented
