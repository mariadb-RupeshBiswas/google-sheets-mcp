"""Authentication helpers using Application Default Credentials (ADC).

Run once to set up credentials:
    gcloud auth login --enable-gdrive-access --update-adc

This writes ADC to ~/.config/gcloud/application_default_credentials.json and
includes the Drive + Sheets scopes automatically via --enable-gdrive-access.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys

import google.auth
import google.auth.credentials
import google.auth.exceptions
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

SCOPES: list[str] = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

_ADC_PATH = os.path.expanduser(
    "~/.config/gcloud/application_default_credentials.json"
)


class AuthError(Exception):
    """Raised when ADC cannot be loaded or is missing required scopes."""


def credentials_exist() -> bool:
    """Return True if an ADC file already exists on disk."""
    return os.path.isfile(_ADC_PATH) or bool(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )


def _gcloud_installed() -> bool:
    """Return True if the gcloud CLI is on PATH."""
    return shutil.which("gcloud") is not None


def ensure_authenticated() -> None:
    """Trigger the gcloud auth flow if no credentials are present.

    Prints a clear status message so the user understands what is happening.
    This is a no-op when credentials already exist.

    Raises:
        AuthError: If gcloud is not installed and no credentials exist.
        AuthError: If the interactive auth flow fails.
    """
    if credentials_exist():
        return

    print(
        "\n"
        "=" * 60 + "\n"
        "Google Sheets MCP — No credentials found!\n"
        "=" * 60 + "\n"
        "\nRunning the authentication setup now…\n",
        file=sys.stderr,
    )

    if not _gcloud_installed():
        raise AuthError(
            "'gcloud' CLI not found on PATH.\n\n"
            "Install the Google Cloud SDK first:\n"
            "  https://cloud.google.com/sdk/docs/install\n\n"
            "Then run:\n"
            "  gcloud auth login --enable-gdrive-access --update-adc\n"
        )

    print(
        "A browser window will open for Google login.\n"
        "Complete the sign-in and then return here.\n",
        file=sys.stderr,
    )
    result = subprocess.run(
        [
            "gcloud",
            "auth",
            "login",
            "--enable-gdrive-access",
            "--update-adc",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise AuthError(
            "Authentication failed (gcloud exited with a non-zero code).\n\n"
            "Try running this manually:\n"
            "  gcloud auth login --enable-gdrive-access --update-adc\n"
        )
    print(
        "\n" + "=" * 60 + "\n"
        "Authentication successful!  Starting the server…\n"
        + "=" * 60 + "\n",
        file=sys.stderr,
    )


def get_credentials() -> google.auth.credentials.Credentials:
    """Load and return refreshed Application Default Credentials.

    Automatically triggers an interactive ``gcloud auth login`` flow when no
    credentials exist (mirrors the bigquery-mcp UX).

    The credentials must have been created with:
        gcloud auth login --enable-gdrive-access --update-adc

    Returns:
        Refreshed google.auth.credentials.Credentials object.

    Raises:
        AuthError: If credentials cannot be found or refreshed.
    """
    ensure_authenticated()

    try:
        creds, project = google.auth.default(scopes=SCOPES)
        logger.debug("Loaded ADC for project: %s", project or "<unknown>")
    except google.auth.exceptions.DefaultCredentialsError as exc:
        raise AuthError(
            "No Application Default Credentials found.\n\n"
            "Run the following command and try again:\n\n"
            "    gcloud auth login --enable-gdrive-access --update-adc\n"
        ) from exc

    if not creds.valid:
        try:
            creds.refresh(Request())
        except google.auth.exceptions.TransportError as exc:
            raise AuthError(f"Could not refresh credentials: {exc}") from exc

    return creds
