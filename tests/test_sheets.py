"""Tests for g_sheet_mcp.sheets module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from googleapiclient.errors import HttpError

from g_sheet_mcp.sheets import (
    SheetsClient,
    _a1,
    _col_to_letter,
    _quote_sheet,
    _validate_render_option,
    spreadsheet_id_from_url,
)
from tests.conftest import SAMPLE_SPREADSHEET_ID, SAMPLE_SPREADSHEET_URL


class TestSpreadsheetIdFromUrl:
    def test_full_url(self):
        result = spreadsheet_id_from_url(SAMPLE_SPREADSHEET_URL)
        assert result == SAMPLE_SPREADSHEET_ID

    def test_bare_id(self):
        result = spreadsheet_id_from_url(SAMPLE_SPREADSHEET_ID)
        assert result == SAMPLE_SPREADSHEET_ID

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="Cannot extract"):
            spreadsheet_id_from_url("https://example.com/not-a-sheet")

    def test_short_string_raises(self):
        with pytest.raises(ValueError):
            spreadsheet_id_from_url("short")


class TestColToLetter:
    @pytest.mark.parametrize(
        "col, expected",
        [
            (1, "A"),
            (26, "Z"),
            (27, "AA"),
            (52, "AZ"),
            (53, "BA"),
        ],
    )
    def test_conversion(self, col, expected):
        assert _col_to_letter(col) == expected


class TestA1Notation:
    def test_basic(self):
        assert _a1(1, 1) == "A1"
        assert _a1(3, 2) == "B3"
        assert _a1(10, 27) == "AA10"


class TestGetSpreadsheetInfo:
    def test_returns_info(self, sheets_client):
        info = sheets_client.get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)
        assert info.title == "Test Spreadsheet"
        assert info.spreadsheet_id == SAMPLE_SPREADSHEET_ID
        assert len(info.sheets) == 2
        assert info.sheets[0].title == "Sheet1"
        assert info.sheets[1].title == "Data"

    def test_sheet_properties(self, sheets_client):
        info = sheets_client.get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)
        sheet = info.sheets[0]
        assert sheet.sheet_id == 0
        assert sheet.index == 0
        assert sheet.row_count == 1000
        assert sheet.column_count == 26

    def test_403_raises_permission_error(self, mock_credentials, mock_sheets_service):
        resp = MagicMock()
        resp.status = 403
        mock_sheets_service.spreadsheets.return_value.get.return_value.execute.side_effect = (
            HttpError(resp=resp, content=b"forbidden")
        )
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        with pytest.raises(PermissionError, match="Access denied"):
            client.get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)

    def test_404_raises_file_not_found(self, mock_credentials, mock_sheets_service):
        resp = MagicMock()
        resp.status = 404
        mock_sheets_service.spreadsheets.return_value.get.return_value.execute.side_effect = (
            HttpError(resp=resp, content=b"not found")
        )
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        with pytest.raises(FileNotFoundError, match="not found"):
            client.get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)


class TestReadRange:
    def test_returns_range_data(self, sheets_client):
        result = sheets_client.read_range(SAMPLE_SPREADSHEET_ID, "Sheet1!A1:D3")
        assert result.row_count == 3
        assert result.column_count == 4
        assert result.values[0] == ["Name", "Age", "City", "Score"]

    def test_sheet_title_extracted(self, sheets_client):
        result = sheets_client.read_range(SAMPLE_SPREADSHEET_ID, "Sheet1!A1:D3")
        assert result.sheet_title == "Sheet1"

    def test_empty_sheet_returns_empty_values(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!A1",
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        result = client.read_range(SAMPLE_SPREADSHEET_ID, "Sheet1!A1")
        assert result.values == []
        assert result.row_count == 0


class TestReadSheet:
    def test_delegates_to_read_range(self, sheets_client):
        result = sheets_client.read_sheet(SAMPLE_SPREADSHEET_ID, "Sheet1")
        assert result.row_count == 3


class TestGetCell:
    def test_single_cell_value(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!B2",
            "values": [["Alice"]],
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        cell = client.get_cell(SAMPLE_SPREADSHEET_ID, "Sheet1", row=2, column=2)
        assert cell.value == "Alice"
        assert cell.a1_notation == "B2"
        assert cell.row == 2
        assert cell.column == 2

    def test_empty_cell_returns_none(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!Z100",
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        cell = client.get_cell(SAMPLE_SPREADSHEET_ID, "Sheet1", row=100, column=26)
        assert cell.value is None


class TestFindInSpreadsheet:
    def test_finds_matching_cell(self, mock_credentials, mock_sheets_service):
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
            "range": "Sheet1!A1:D3",
            "values": [
                ["Name", "Age", "City"],
                ["Alice", "30", "New York"],
            ],
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        results = client.find_in_spreadsheet(SAMPLE_SPREADSHEET_ID, "Alice")
        assert len(results) == 1
        assert results[0].matched_value == "Alice"
        assert results[0].row == 2
        assert results[0].column == 1

    def test_case_insensitive_match(self, mock_credentials, mock_sheets_service):
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
            "range": "Sheet1!A1:A1",
            "values": [["HELLO WORLD"]],
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        results = client.find_in_spreadsheet(SAMPLE_SPREADSHEET_ID, "hello", case_sensitive=False)
        assert len(results) == 1


class TestBatchReadRanges:
    def test_returns_multiple_ranges(self, sheets_client):
        results = sheets_client.batch_read_ranges(
            SAMPLE_SPREADSHEET_ID, ["Sheet1!A1:B2", "Data!C1:C3"]
        )
        assert len(results) == 2
        assert results[0].values == [["A1", "B1"], ["A2", "B2"]]
        assert results[1].values == [["C1"], ["C2"], ["C3"]]

    def test_empty_ranges_raises(self, sheets_client):
        with pytest.raises(ValueError, match="at least one"):
            sheets_client.batch_read_ranges(SAMPLE_SPREADSHEET_ID, [])


class TestQuoteSheet:
    def test_simple_name_wrapped(self):
        assert _quote_sheet("Sheet1") == "'Sheet1'"

    def test_name_with_spaces(self):
        assert _quote_sheet("My Sheet") == "'My Sheet'"

    def test_name_with_single_quote_escaped(self):
        assert _quote_sheet("Bob's Data") == "'Bob''s Data'"

    def test_empty_string(self):
        assert _quote_sheet("") == "''"


class TestValidateRenderOption:
    def test_valid_formatted(self):
        _validate_render_option("FORMATTED_VALUE")  # no exception

    def test_valid_unformatted(self):
        _validate_render_option("UNFORMATTED_VALUE")  # no exception

    def test_valid_formula(self):
        _validate_render_option("FORMULA")  # no exception

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid value_render_option"):
            _validate_render_option("RAW")


class TestInputValidation:
    def test_empty_spreadsheet_id_raises(self, sheets_client):
        with pytest.raises(ValueError, match="non-empty"):
            sheets_client.get_spreadsheet_info("")

    def test_whitespace_spreadsheet_id_raises(self, sheets_client):
        with pytest.raises(ValueError, match="non-empty"):
            sheets_client.get_spreadsheet_info("   ")

    def test_empty_range_notation_raises(self, sheets_client):
        with pytest.raises(ValueError, match="non-empty"):
            sheets_client.read_range(SAMPLE_SPREADSHEET_ID, "")

    def test_empty_sheet_title_raises(self, sheets_client):
        with pytest.raises(ValueError, match="non-empty"):
            sheets_client.read_sheet(SAMPLE_SPREADSHEET_ID, "")

    def test_get_cell_row_zero_raises(self, sheets_client):
        with pytest.raises(ValueError, match="row must be >= 1"):
            sheets_client.get_cell(SAMPLE_SPREADSHEET_ID, "Sheet1", row=0, column=1)

    def test_get_cell_negative_row_raises(self, sheets_client):
        with pytest.raises(ValueError, match="row must be >= 1"):
            sheets_client.get_cell(SAMPLE_SPREADSHEET_ID, "Sheet1", row=-1, column=1)

    def test_get_cell_column_zero_raises(self, sheets_client):
        with pytest.raises(ValueError, match="column must be >= 1"):
            sheets_client.get_cell(SAMPLE_SPREADSHEET_ID, "Sheet1", row=1, column=0)

    def test_find_empty_query_raises(self, sheets_client):
        with pytest.raises(ValueError, match="non-empty"):
            sheets_client.find_in_spreadsheet(SAMPLE_SPREADSHEET_ID, "")

    def test_find_zero_max_results_raises(self, sheets_client):
        with pytest.raises(ValueError, match="max_results must be > 0"):
            sheets_client.find_in_spreadsheet(SAMPLE_SPREADSHEET_ID, "x", max_results=0)


class TestFindInSpreadsheetUnknownSheet:
    def test_raises_lookup_error_for_unknown_sheet(self, mock_credentials, mock_sheets_service):
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
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        with pytest.raises(LookupError, match="NoSuchSheet.*not found"):
            client.find_in_spreadsheet(SAMPLE_SPREADSHEET_ID, "x", sheet_title="NoSuchSheet")


class TestHttpErrorHandling:
    def _make_http_error(self, status: int) -> HttpError:
        resp = MagicMock()
        resp.status = status
        return HttpError(resp=resp, content=b"error")

    def test_429_raises_runtime_error(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.get.return_value.execute.side_effect = (
            self._make_http_error(429)
        )
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        with pytest.raises(RuntimeError, match="rate limit"):
            client.get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)

    def test_500_raises_runtime_error(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.get.return_value.execute.side_effect = (
            self._make_http_error(500)
        )
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        with pytest.raises(RuntimeError, match="server error"):
            client.get_spreadsheet_info(SAMPLE_SPREADSHEET_ID)


class TestReadSheetAsRecords:
    def test_returns_list_of_dicts(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "'Sheet1'",
            "values": [
                ["Name", "Age", "City"],
                ["Alice", "30", "New York"],
                ["Bob", "25", "London"],
            ],
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        records = client.read_sheet_as_records(SAMPLE_SPREADSHEET_ID, "Sheet1")
        assert len(records) == 2
        assert records[0] == {"Name": "Alice", "Age": "30", "City": "New York"}
        assert records[1] == {"Name": "Bob", "Age": "25", "City": "London"}

    def test_short_row_fills_none(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "'Sheet1'",
            "values": [
                ["A", "B", "C"],
                ["x"],  # only one cell — B and C should be None
            ],
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        records = client.read_sheet_as_records(SAMPLE_SPREADSHEET_ID, "Sheet1")
        assert records[0] == {"A": "x", "B": None, "C": None}

    def test_empty_sheet_returns_empty_list(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "'Sheet1'",
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        records = client.read_sheet_as_records(SAMPLE_SPREADSHEET_ID, "Sheet1")
        assert records == []

    def test_max_rows_respected(self, mock_credentials, mock_sheets_service):
        mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "'Sheet1'",
            "values": [["H"]] + [["r"] for _ in range(10)],
        }
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)

        records = client.read_sheet_as_records(SAMPLE_SPREADSHEET_ID, "Sheet1", max_rows=3)
        assert len(records) == 3

    def test_zero_max_rows_raises(self, mock_credentials, mock_sheets_service):
        with patch("g_sheet_mcp.sheets.build", return_value=mock_sheets_service):
            client = SheetsClient(mock_credentials)
        with pytest.raises(ValueError, match="max_rows must be > 0"):
            client.read_sheet_as_records(SAMPLE_SPREADSHEET_ID, "Sheet1", max_rows=0)
