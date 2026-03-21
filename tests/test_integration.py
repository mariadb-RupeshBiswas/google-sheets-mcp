"""Integration tests – require real ADC credentials and network access.

Spreadsheet under test:
    https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID
    Title: Example Spreadsheet
    Tabs:  Example Sheet 1 … Example Sheet 8  (space in name — tests quoting)

Run with:
    INTEGRATION=1 uv run pytest tests/test_integration.py -v -s

These tests hit the live Google Sheets API and are skipped unless the
INTEGRATION environment variable is set to "1".
"""

from __future__ import annotations

import os

import pytest

SAMPLE_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "EXAMPLE_SPREADSHEET_ID/edit?gid=0#gid=0"
)
SAMPLE_ID = "EXAMPLE_SPREADSHEET_ID"

pytestmark = pytest.mark.skipif(
    os.environ.get("INTEGRATION") != "1",
    reason="Set INTEGRATION=1 to run live API tests",
)


@pytest.fixture(scope="module")
def client():
    from g_sheet_mcp.auth import get_credentials
    from g_sheet_mcp.sheets import SheetsClient

    creds = get_credentials()
    return SheetsClient(creds)


@pytest.fixture(scope="module")
def spreadsheet_info(client):
    return client.get_spreadsheet_info(SAMPLE_ID)


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class TestLiveMetadata:
    def test_get_info_by_id(self, spreadsheet_info):
        print(f"\nTitle: {spreadsheet_info.title}")
        print(f"Sheets ({len(spreadsheet_info.sheets)}): {[s.title for s in spreadsheet_info.sheets]}")
        assert spreadsheet_info.spreadsheet_id == SAMPLE_ID
        assert spreadsheet_info.title == "Example Spreadsheet"

    def test_get_info_by_url(self, client):
        info = client.get_spreadsheet_info(
            "https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit"
        )
        assert info.spreadsheet_id == SAMPLE_ID

    def test_has_eight_tabs(self, spreadsheet_info):
        assert len(spreadsheet_info.sheets) == 8
        titles = [s.title for s in spreadsheet_info.sheets]
        assert titles == [f"Test Case {i}" for i in range(1, 9)]

    def test_sheet_names_contain_spaces(self, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            assert " " in sheet.title, f"Expected space in '{sheet.title}'"

    def test_all_sheets_are_grid_type(self, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            assert sheet.sheet_type == "GRID"

    def test_sheet_properties_populated(self, spreadsheet_info):
        s = spreadsheet_info.sheets[0]
        assert s.row_count > 0
        assert s.column_count > 0


# ---------------------------------------------------------------------------
# Reading all 8 tabs
# ---------------------------------------------------------------------------


class TestReadAllTabs:
    def test_read_every_tab(self, client, spreadsheet_info):
        """Read data from every sheet — verifies sheet-name quoting works for spaces."""
        for sheet in spreadsheet_info.sheets:
            data = client.read_sheet(SAMPLE_ID, sheet.title)
            print(f"\n  '{sheet.title}': {data.row_count} rows × {data.column_count} cols")
            assert data.sheet_title == sheet.title

    def test_first_tab_has_expected_headers(self, client):
        data = client.read_sheet(SAMPLE_ID, "Example Sheet 1")
        assert data.values, "Sheet should not be empty"
        headers = data.values[0]
        assert "example_id" in headers
        assert "example_name" in headers
        assert "example_value_usd" in headers

    def test_first_tab_column_count(self, client):
        data = client.read_sheet(SAMPLE_ID, "Example Sheet 1")
        assert data.column_count == 53

    def test_each_tab_has_data_rows(self, client, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            data = client.read_sheet(SAMPLE_ID, sheet.title)
            assert data.row_count >= 1, f"'{sheet.title}' appears empty"


# ---------------------------------------------------------------------------
# Range reads
# ---------------------------------------------------------------------------


class TestReadRange:
    def test_read_first_four_columns(self, client):
        data = client.read_range(SAMPLE_ID, "'Example Sheet 1'!A1:D5")
        assert data.row_count <= 5
        assert data.column_count == 4

    def test_read_single_column(self, client):
        data = client.read_range(SAMPLE_ID, "'Example Sheet 1'!A:A")
        assert data.column_count == 1
        assert data.values[0][0] == "example_id"

    def test_read_header_row_only(self, client):
        data = client.read_range(SAMPLE_ID, "'Example Sheet 1'!A1:AZ1")
        assert data.row_count == 1
        assert len(data.values[0]) == 52  # actual column count in the sheet


# ---------------------------------------------------------------------------
# Single cell
# ---------------------------------------------------------------------------


class TestGetCell:
    def test_a1_is_example_id(self, client):
        cell = client.get_cell(SAMPLE_ID, "Example Sheet 1", row=1, column=1)
        print(f"\nA1 = {cell.value!r}")
        assert cell.value == "example_id"
        assert cell.a1_notation == "A1"

    def test_b1_is_example_name(self, client):
        cell = client.get_cell(SAMPLE_ID, "Example Sheet 1", row=1, column=2)
        assert cell.value == "example_name"
        assert cell.a1_notation == "B1"

    def test_out_of_range_cell_raises_error(self, client):
        from googleapiclient.errors import HttpError
        with pytest.raises(HttpError, match="exceeds grid limits"):
            client.get_cell(SAMPLE_ID, "Example Sheet 1", row=999, column=999)


# ---------------------------------------------------------------------------
# read_sheet_as_records
# ---------------------------------------------------------------------------


class TestReadSheetAsRecords:
    def test_returns_list_of_dicts(self, client):
        records = client.read_sheet_as_records(SAMPLE_ID, "Example Sheet 1")
        print(f"\nrecords count: {len(records)}")
        assert isinstance(records, list)
        assert len(records) >= 1
        first = records[0]
        assert isinstance(first, dict)
        assert "example_id" in first
        assert "example_value_usd" in first

    def test_all_records_have_same_keys(self, client):
        records = client.read_sheet_as_records(SAMPLE_ID, "Example Sheet 1")
        if len(records) > 1:
            keys0 = set(records[0].keys())
            for rec in records[1:]:
                assert set(rec.keys()) == keys0

    def test_max_rows_respected(self, client):
        records = client.read_sheet_as_records(SAMPLE_ID, "Example Sheet 1", max_rows=1)
        assert len(records) <= 1

    def test_works_on_all_tabs(self, client, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            records = client.read_sheet_as_records(SAMPLE_ID, sheet.title)
            print(f"\n  '{sheet.title}' → {len(records)} records")


# ---------------------------------------------------------------------------
# Batch read
# ---------------------------------------------------------------------------


class TestBatchRead:
    def test_batch_two_tabs(self, client):
        results = client.batch_read_ranges(
            SAMPLE_ID,
            ["'Example Sheet 1'!A1:D2", "'Example Sheet 2'!A1:D2"],
        )
        assert len(results) == 2
        for r in results:
            assert r.row_count >= 1

    def test_batch_headers_of_all_tabs(self, client, spreadsheet_info):
        ranges = [f"'{s.title}'!A1:AZ1" for s in spreadsheet_info.sheets]
        results = client.batch_read_ranges(SAMPLE_ID, ranges)
        assert len(results) == 8
        # Check that sheets with data have the expected header
        sheets_with_data = [r for r in results if r.row_count > 0]
        assert len(sheets_with_data) >= 1, "At least one sheet should have data"
        for r in sheets_with_data:
            assert r.values[0][0] == "example_id"


# ---------------------------------------------------------------------------
# Find
# ---------------------------------------------------------------------------


class TestFindInSpreadsheet:
    def test_find_example_id_in_first_tab(self, client):
        results = client.find_in_spreadsheet(
            SAMPLE_ID, "example_id", sheet_title="Example Sheet 1"
        )
        assert len(results) >= 1
        assert results[0].matched_value == "example_id"
        assert results[0].row == 1

    def test_find_case_insensitive(self, client):
        results = client.find_in_spreadsheet(
            SAMPLE_ID, "EXAMPLE_ID", sheet_title="Example Sheet 1", case_sensitive=False
        )
        assert len(results) >= 1

    def test_find_nonexistent_returns_empty(self, client):
        results = client.find_in_spreadsheet(
            SAMPLE_ID, "ZZZNOMATCH_XYZ_123456", sheet_title="Example Sheet 1"
        )
        assert results == []

    def test_find_unknown_sheet_raises(self, client):
        with pytest.raises(LookupError):
            client.find_in_spreadsheet(SAMPLE_ID, "example_id", sheet_title="DoesNotExist")


# ---------------------------------------------------------------------------
# URL handling
# ---------------------------------------------------------------------------


class TestUrlHandling:
    def test_full_url_accepted(self, client):
        info = client.get_spreadsheet_info(SAMPLE_URL)
        assert info.spreadsheet_id == SAMPLE_ID

    def test_bare_id_accepted(self, client):
        info = client.get_spreadsheet_info(SAMPLE_ID)
        assert info.spreadsheet_id == SAMPLE_ID
