"""Tests for g_sheet_mcp.server MCP tool functions."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.conftest import SAMPLE_SPREADSHEET_ID, SAMPLE_SPREADSHEET_URL


@pytest.fixture(autouse=True)
def reset_client():
    """Reset the module-level _client between tests."""
    import g_sheet_mcp.server as srv

    srv._client = None
    yield
    srv._client = None


@pytest.fixture()
def patched_client(sheets_client):
    """Patch server._get_client to return the mocked sheets_client."""
    import g_sheet_mcp.server as srv

    with patch.object(srv, "_get_client", return_value=sheets_client):
        yield sheets_client


class TestGetSpreadsheetInfoTool:
    def test_with_url(self, patched_client):
        from g_sheet_mcp.server import get_spreadsheet_info

        result = get_spreadsheet_info(SAMPLE_SPREADSHEET_URL)
        assert result["title"] == "Test Spreadsheet"
        assert result["spreadsheet_id"] == SAMPLE_SPREADSHEET_ID
        assert len(result["sheets"]) == 2

    def test_with_bare_id(self, patched_client):
        from g_sheet_mcp.server import get_spreadsheet_info

        result = get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)
        assert result["title"] == "Test Spreadsheet"


class TestListSheetsTool:
    def test_returns_sheet_list(self, patched_client):
        from g_sheet_mcp.server import list_sheets

        result = list_sheets(SAMPLE_SPREADSHEET_URL)
        assert isinstance(result, list)
        assert len(result) == 2
        titles = [s["title"] for s in result]
        assert "Sheet1" in titles
        assert "Data" in titles


class TestReadRangeTool:
    def test_basic_range(self, patched_client):
        from g_sheet_mcp.server import read_range

        result = read_range(SAMPLE_SPREADSHEET_URL, "Sheet1!A1:D3")
        assert result["row_count"] == 3
        assert result["values"][0] == ["Name", "Age", "City", "Score"]

    def test_render_option_forwarded(self, patched_client):
        from g_sheet_mcp.server import read_range

        result = read_range(SAMPLE_SPREADSHEET_URL, "Sheet1!A1:D3", "UNFORMATTED_VALUE")
        assert "values" in result


class TestReadSheetTool:
    def test_reads_sheet(self, patched_client):
        from g_sheet_mcp.server import read_sheet

        result = read_sheet(SAMPLE_SPREADSHEET_URL, "Sheet1")
        assert result["sheet_title"] == "Sheet1"
        assert result["row_count"] == 3


class TestGetCellTool:
    def test_reads_cell(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!A1",
            "values": [["Header"]],
        }
        from g_sheet_mcp.sheets import SheetsClient

        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        import g_sheet_mcp.server as srv

        with patch.object(srv, "_get_client", return_value=client):
            from g_sheet_mcp.server import get_cell

            result = get_cell(SAMPLE_SPREADSHEET_ID, "Sheet1", row=1, column=1)
        assert result["value"] == "Header"
        assert result["a1_notation"] == "A1"


class TestFindInSpreadsheetTool:
    def test_finds_cell(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "spreadsheetId": SAMPLE_SPREADSHEET_ID,
            "properties": {"title": "T", "locale": "en_US", "timeZone": "UTC"},
            "sheets": [
                {
                    "properties": {
                        "sheetId": 0,
                        "title": "Sheet1",
                        "index": 0,
                        "sheetType": "GRID",
                        "gridProperties": {"rowCount": 10, "columnCount": 5},
                    }
                }
            ],
        }
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!A1:B2",
            "values": [["hello", "world"], ["foo", "bar"]],
        }
        from g_sheet_mcp.sheets import SheetsClient

        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        import g_sheet_mcp.server as srv

        with patch.object(srv, "_get_client", return_value=client):
            from g_sheet_mcp.server import find_in_spreadsheet

            results = find_in_spreadsheet(SAMPLE_SPREADSHEET_ID, "hello")
        assert len(results) == 1
        assert results[0]["matched_value"] == "hello"


class TestBatchReadRangesTool:
    def test_batch_read(self, patched_client):
        from g_sheet_mcp.server import batch_read_ranges

        results = batch_read_ranges(
            SAMPLE_SPREADSHEET_URL, ["Sheet1!A1:B2", "Data!C1:C3"]
        )
        assert len(results) == 2


class TestResolveId:
    def test_url_resolved(self):
        from g_sheet_mcp.server import _resolve_id

        assert _resolve_id(SAMPLE_SPREADSHEET_URL) == SAMPLE_SPREADSHEET_ID

    def test_bare_id_passthrough(self):
        from g_sheet_mcp.server import _resolve_id

        assert _resolve_id(SAMPLE_SPREADSHEET_ID) == SAMPLE_SPREADSHEET_ID
