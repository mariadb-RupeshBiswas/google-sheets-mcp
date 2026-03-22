"""Shared pytest fixtures for the g-sheet-mcp test suite."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

SAMPLE_SPREADSHEET_ID = os.environ.get("TEST_SPREADSHEET_ID", "test_spreadsheet_id_placeholder")
SAMPLE_SPREADSHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{SAMPLE_SPREADSHEET_ID}/edit?gid=0#gid=0"
)

FAKE_SPREADSHEET_RESPONSE = {
    "spreadsheetId": SAMPLE_SPREADSHEET_ID,
    "properties": {
        "title": "Test Spreadsheet",
        "locale": "en_US",
        "timeZone": "America/New_York",
    },
    "sheets": [
        {
            "properties": {
                "sheetId": 0,
                "title": "Sheet1",
                "index": 0,
                "sheetType": "GRID",
                "gridProperties": {"rowCount": 1000, "columnCount": 26},
            }
        },
        {
            "properties": {
                "sheetId": 123456,
                "title": "Data",
                "index": 1,
                "sheetType": "GRID",
                "gridProperties": {"rowCount": 500, "columnCount": 10},
            }
        },
    ],
}

FAKE_VALUES_RESPONSE = {
    "range": "Sheet1!A1:D3",
    "majorDimension": "ROWS",
    "values": [
        ["Name", "Age", "City", "Score"],
        ["Alice", "30", "New York", "95"],
        ["Bob", "25", "London", "87"],
    ],
}

FAKE_BATCH_VALUES_RESPONSE = {
    "spreadsheetId": SAMPLE_SPREADSHEET_ID,
    "valueRanges": [
        {
            "range": "Sheet1!A1:B2",
            "majorDimension": "ROWS",
            "values": [["A1", "B1"], ["A2", "B2"]],
        },
        {
            "range": "Data!C1:C3",
            "majorDimension": "ROWS",
            "values": [["C1"], ["C2"], ["C3"]],
        },
    ],
}


@pytest.fixture()
def mock_credentials():
    """Return a mock google.auth.credentials.Credentials object."""
    creds = MagicMock()
    creds.valid = True
    return creds


@pytest.fixture()
def mock_sheets_service():
    """Return a mock googleapiclient service object wired to return fake data."""
    service = MagicMock()

    # spreadsheets().get().execute()
    service.spreadsheets.return_value.get.return_value.execute.return_value = (
        FAKE_SPREADSHEET_RESPONSE
    )

    # spreadsheets().values().get().execute()
    service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = (
        FAKE_VALUES_RESPONSE
    )

    # spreadsheets().values().batchGet().execute()
    service.spreadsheets.return_value.values.return_value.batchGet.return_value.execute.return_value = (
        FAKE_BATCH_VALUES_RESPONSE
    )

    return service


@pytest.fixture()
def sheets_client(mock_credentials, mock_sheets_service):
    """Return a SheetsClient with the Google API service mocked out."""
    from g_sheet_mcp.sheets import SheetsClient

    with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
        client = SheetsClient(mock_credentials)
    return client
