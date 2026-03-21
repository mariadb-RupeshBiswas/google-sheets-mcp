# Authentication Guide

## How it works

This server uses **Application Default Credentials (ADC)** — the same secure mechanism used by
Google Cloud services. No service account JSON files, no hardcoded secrets.

```
gcloud auth login --enable-gdrive-access --update-adc
        ↓
~/.config/gcloud/application_default_credentials.json  (written once)
        ↓
google.auth.default(scopes=[spreadsheets.readonly, drive.readonly])  (loaded at runtime)
        ↓
SheetsClient → Google Sheets API v4
```

---

## Automatic flow

When the server starts and no credentials exist, it will:

1. Print a clear message explaining what is happening
2. Run `gcloud auth login --enable-gdrive-access --update-adc` automatically
3. Open your browser for Google sign-in
4. Continue once authentication completes

```
============================================================
Google Sheets MCP — No credentials found!
============================================================

A browser window will open for Google login.
Complete the sign-in and then return here.

[Browser opens]

============================================================
Authentication successful!  Starting the server…
============================================================
```

If you prefer to authenticate manually before starting:

```bash
gcloud auth login --enable-gdrive-access --update-adc
```

---

## Required scopes

The `--enable-gdrive-access` flag ensures these scopes are included:

| Scope | Purpose |
|---|---|
| `spreadsheets.readonly` | Read spreadsheet data and metadata |
| `drive.readonly` | Enumerate Drive files (needed to resolve spreadsheet names) |

> **Why Drive scope?** The Sheets API alone cannot list Drive files or resolve spreadsheet names.
> The Drive read-only scope is the minimum required alongside Sheets.

---

## Credential locations

The server checks for credentials in this order:

| Priority | Location |
|---|---|
| 1 | `$GOOGLE_APPLICATION_CREDENTIALS` environment variable |
| 2 | `~/.config/gcloud/application_default_credentials.json` (ADC file) |

---

## Re-authenticating

ADC tokens expire after a while. To refresh:

```bash
gcloud auth login --enable-gdrive-access --update-adc
```

Or revoke and re-authenticate:

```bash
gcloud auth revoke --all
gcloud auth login --enable-gdrive-access --update-adc
```

---

## Service accounts (CI/CD)

For automated environments without a browser:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account_key.json
```

The service account must have the spreadsheet shared with its email address
(e.g. `my-sa@project.iam.gserviceaccount.com`).

---

## Access control

ADC proves **who you are** but Google Sheets **share settings** still apply.

- Your Google account must have at least **Viewer** access to any spreadsheet
- Public spreadsheets (shared with "Anyone with the link") work automatically
- Private spreadsheets require explicit sharing with your account

---

## Security notes

- Credentials are stored only by the Google Cloud SDK — never by this server
- The server is **read-only** by design — it requests only `*.readonly` scopes
- Tokens are auto-refreshed at runtime; no manual token management required
- You can revoke access at any time from [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
