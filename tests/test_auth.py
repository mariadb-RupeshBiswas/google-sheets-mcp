"""Tests for g_sheet_mcp.auth module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from g_sheet_mcp.auth import (
    AuthError,
    credentials_exist,
    credentials_fingerprint,
    ensure_authenticated,
    get_credentials,
)


class TestCredentialsFingerprint:
    def test_uses_adc_path_mtime_when_present(self, tmp_path):
        fake_adc = tmp_path / "application_default_credentials.json"
        fake_adc.write_text("{}")
        with (
            patch("g_sheet_mcp.auth._ADC_PATH", str(fake_adc)),
            patch.dict("os.environ", {}, clear=True),
        ):
            path, mtime = credentials_fingerprint()
        assert path == str(fake_adc)
        assert isinstance(mtime, int)

    def test_uses_google_application_credentials_path(self, tmp_path):
        fake_adc = tmp_path / "service-account.json"
        fake_adc.write_text("{}")
        with patch.dict(
            "os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": str(fake_adc)}, clear=True
        ):
            path, mtime = credentials_fingerprint()
        assert path == str(fake_adc)
        assert isinstance(mtime, int)


class TestCredentialsExist:
    def test_returns_true_when_adc_file_present(self, tmp_path):
        fake_adc = tmp_path / "application_default_credentials.json"
        fake_adc.write_text("{}")
        with (
            patch("g_sheet_mcp.auth._ADC_PATH", str(fake_adc)),
            patch.dict("os.environ", {}, clear=True),
        ):
            assert credentials_exist() is True

    def test_returns_false_when_no_adc_file(self, tmp_path):
        missing = str(tmp_path / "missing.json")
        with (
            patch("g_sheet_mcp.auth._ADC_PATH", missing),
            patch.dict("os.environ", {}, clear=True),
        ):
            assert credentials_exist() is False

    def test_returns_true_when_google_env_var_set(self, tmp_path):
        missing = str(tmp_path / "missing.json")
        with (
            patch("g_sheet_mcp.auth._ADC_PATH", missing),
            patch.dict("os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": "/some/key.json"}),
        ):
            assert credentials_exist() is True


class TestEnsureAuthenticated:
    def test_noop_when_credentials_exist(self):
        with patch("g_sheet_mcp.auth.credentials_exist", return_value=True) as mock_check:
            ensure_authenticated()
        mock_check.assert_called_once()

    def test_raises_when_gcloud_not_installed(self):
        with (
            patch("g_sheet_mcp.auth.credentials_exist", return_value=False),
            patch("g_sheet_mcp.auth._gcloud_installed", return_value=False),
            pytest.raises(AuthError, match="gcloud.*not found"),
        ):
            ensure_authenticated()

    def test_raises_when_gcloud_auth_exits_nonzero(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        with (
            patch("g_sheet_mcp.auth.credentials_exist", return_value=False),
            patch("g_sheet_mcp.auth._gcloud_installed", return_value=True),
            patch("g_sheet_mcp.auth.subprocess.run", return_value=mock_result),
            pytest.raises(AuthError, match="Authentication failed"),
        ):
            ensure_authenticated()

    def test_succeeds_when_gcloud_auth_returns_zero(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        with (
            patch("g_sheet_mcp.auth.credentials_exist", return_value=False),
            patch("g_sheet_mcp.auth._gcloud_installed", return_value=True),
            patch("g_sheet_mcp.auth.subprocess.run", return_value=mock_result),
        ):
            ensure_authenticated()  # must not raise


class TestGetCredentials:
    def _patch_ensure(self):
        return patch("g_sheet_mcp.auth.ensure_authenticated")

    def test_returns_valid_credentials(self):
        mock_creds = MagicMock()
        mock_creds.valid = True

        with (
            self._patch_ensure(),
            patch("g_sheet_mcp.auth.google.auth.default", return_value=(mock_creds, "proj")),
        ):
            creds = get_credentials()

        assert creds is mock_creds

    def test_refreshes_expired_credentials(self):
        mock_creds = MagicMock()
        mock_creds.valid = False

        with (
            self._patch_ensure(),
            patch("g_sheet_mcp.auth.google.auth.default", return_value=(mock_creds, "proj")),
            patch("g_sheet_mcp.auth.Request") as mock_request,
        ):
            creds = get_credentials()
            mock_creds.refresh.assert_called_once_with(mock_request())

        assert creds is mock_creds

    def test_raises_auth_error_when_no_adc(self):
        import google.auth.exceptions

        with (
            self._patch_ensure(),
            patch(
                "g_sheet_mcp.auth.google.auth.default",
                side_effect=google.auth.exceptions.DefaultCredentialsError("no creds"),
            ),
            pytest.raises(AuthError, match="gcloud auth login"),
        ):
            get_credentials()

    def test_raises_auth_error_on_refresh_failure(self):
        import google.auth.exceptions

        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.refresh.side_effect = google.auth.exceptions.TransportError("network")

        with (
            self._patch_ensure(),
            patch("g_sheet_mcp.auth.google.auth.default", return_value=(mock_creds, "proj")),
            patch("g_sheet_mcp.auth.Request"),
            pytest.raises(AuthError, match="refresh"),
        ):
            get_credentials()

    def test_raises_auth_error_on_generic_google_auth_failure(self):
        import google.auth.exceptions

        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.refresh.side_effect = google.auth.exceptions.RefreshError("revoked")

        with (
            self._patch_ensure(),
            patch("g_sheet_mcp.auth.google.auth.default", return_value=(mock_creds, "proj")),
            patch("g_sheet_mcp.auth.Request"),
            pytest.raises(AuthError, match="gcloud auth login"),
        ):
            get_credentials()
