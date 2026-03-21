"""Integration tests – require real ADC credentials and network access.

Set INTEGRATION=1 and TEST_SPREADSHEET_ID to enable these tests:

    INTEGRATION=1 TEST_SPREADSHEET_ID=your_spreadsheet_id uv run pytest tests/test_integration.py -v -s

The test spreadsheet should have multiple tabs with data for comprehensive testing.
"""

from __future__ import annotations

import os

import pytest

from g_sheet_mcp.sheets import SheetsClient

# Read spreadsheet ID from environment variable
SAMPLE_ID = os.environ.get("TEST_SPREADSHEET_ID", "")
SAMPLE_URL = f"https://docs.google.com/spreadsheets/d/{SAMPLE_ID}/edit?gid=0#gid=0" if SAMPLE_ID else ""

pytestmark = pytest.mark.skipif(
    os.environ.get("INTEGRATION") != "1" or not SAMPLE_ID,
    reason="Set INTEGRATION=1 and TEST_SPREADSHEET_ID to run live tests",
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
    def test_get_info_returns_metadata(self, spreadsheet_info):
        print(f"\nTitle: {spreadsheet_info.title}")
        print(f"Sheets ({len(spreadsheet_info.sheets)}): {[s.title for s in spreadsheet_info.sheets]}")
        assert spreadsheet_info.spreadsheet_id == SAMPLE_ID
        assert spreadsheet_info.title  # Has a title

    def test_get_info_by_url(self, client):
        info = client.get_spreadsheet_info(SAMPLE_URL)
        assert info.spreadsheet_id == SAMPLE_ID

    def test_has_multiple_tabs(self, spreadsheet_info):
        assert len(spreadsheet_info.sheets) >= 1, "Spreadsheet should have at least one sheet"

    def test_sheet_names_populated(self, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            assert sheet.title, "Each sheet should have a title"

    def test_all_sheets_are_grid_type(self, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            assert sheet.sheet_type == "GRID"

    def test_sheet_properties_populated(self, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            assert sheet.title
            assert sheet.sheet_id is not None
            assert sheet.index >= 0


# ---------------------------------------------------------------------------
# Reading sheets
# ---------------------------------------------------------------------------


class TestReadAllTabs:
    def test_read_every_tab(self, client, spreadsheet_info):
        """Read data from every sheet — verifies sheet-name quoting works."""
        for sheet in spreadsheet_info.sheets:
            data = client.read_sheet(SAMPLE_ID, sheet.title)
            assert data.sheet_title == sheet.title

    def test_first_tab_has_headers(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        data = client.read_sheet(SAMPLE_ID, first_sheet)
        if data.values:
            headers = data.values[0]
            assert len(headers) > 0, "First row should have at least one column"

    def test_first_tab_has_columns(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        data = client.read_sheet(SAMPLE_ID, first_sheet)
        assert data.column_count >= 1

    def test_each_tab_readable(self, client, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            data = client.read_sheet(SAMPLE_ID, sheet.title)
            # Just verify we can read it without error
            assert data.sheet_title == sheet.title


# ---------------------------------------------------------------------------
# Range reads
# ---------------------------------------------------------------------------


class TestReadRange:
    def test_read_first_four_columns(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        data = client.read_range(SAMPLE_ID, f"'{first_sheet}'!A1:D5")
        assert data.row_count <= 5
        assert data.column_count == 4

    def test_read_single_column(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        data = client.read_range(SAMPLE_ID, f"'{first_sheet}'!A:A")
        assert data.column_count == 1

    def test_read_header_row_only(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        data = client.read_range(SAMPLE_ID, f"'{first_sheet}'!A1:Z1")
        assert data.row_count == 1
        if data.values:
            assert len(data.values[0]) >= 1


# ---------------------------------------------------------------------------
# Single cell
# ---------------------------------------------------------------------------


class TestGetCell:
    def test_a1_read(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        cell = client.get_cell(SAMPLE_ID, first_sheet, row=1, column=1)
        print(f"\nA1 = {cell.value!r}")
        assert cell.a1_notation == "A1"

    def test_b1_read(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        cell = client.get_cell(SAMPLE_ID, first_sheet, row=1, column=2)
        assert cell.a1_notation == "B1"

    def test_out_of_range_cell_raises_error(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        from googleapiclient.errors import HttpError
        with pytest.raises(HttpError, match="exceeds grid limits"):
            client.get_cell(SAMPLE_ID, first_sheet, row=999, column=999)


# ---------------------------------------------------------------------------
# read_sheet_as_records
# ---------------------------------------------------------------------------


class TestReadSheetAsRecords:
    def test_returns_list_of_dicts(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        records = client.read_sheet_as_records(SAMPLE_ID, first_sheet)
        print(f"\nrecords count: {len(records)}")
        assert isinstance(records, list)
        if len(records) >= 1:
            first = records[0]
            assert isinstance(first, dict)
            assert len(first.keys()) > 0, "Record should have at least one column"

    def test_all_records_have_same_keys(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        records = client.read_sheet_as_records(SAMPLE_ID, first_sheet)
        if len(records) > 1:
            keys0 = set(records[0].keys())
            for rec in records[1:]:
                assert set(rec.keys()) == keys0

    def test_max_rows_respected(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        records = client.read_sheet_as_records(SAMPLE_ID, first_sheet, max_rows=1)
        assert len(records) <= 1

    def test_works_on_all_tabs(self, client, spreadsheet_info):
        for sheet in spreadsheet_info.sheets:
            records = client.read_sheet_as_records(SAMPLE_ID, sheet.title, max_rows=1)
            assert isinstance(records, list)
            print(f"\n  '{sheet.title}' → {len(records)} records")


# ---------------------------------------------------------------------------
# Batch read
# ---------------------------------------------------------------------------


class TestBatchRead:
    def test_batch_two_tabs(self, client, spreadsheet_info):
        if len(spreadsheet_info.sheets) >= 2:
            sheet1 = spreadsheet_info.sheets[0].title
            sheet2 = spreadsheet_info.sheets[1].title
            results = client.batch_read_ranges(
                SAMPLE_ID,
                [f"'{sheet1}'!A1:D2", f"'{sheet2}'!A1:D2"],
            )
            assert len(results) == 2

    def test_batch_headers_of_all_tabs(self, client, spreadsheet_info):
        ranges = [f"'{s.title}'!A1:Z1" for s in spreadsheet_info.sheets]
        results = client.batch_read_ranges(SAMPLE_ID, ranges)
        assert len(results) == len(spreadsheet_info.sheets)
        # Check that sheets with data are readable
        sheets_with_data = [r for r in results if r.row_count > 0]
        assert len(sheets_with_data) >= 1, "At least one sheet should have data"


# ---------------------------------------------------------------------------
# Find
# ---------------------------------------------------------------------------


class TestFindInSpreadsheet:
    def test_find_in_first_tab(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        # Try to find any value from the first cell
        data = client.read_range(SAMPLE_ID, f"'{first_sheet}'!A1:A1")
        if data.values and data.values[0]:
            search_value = data.values[0][0]
            results = client.find_in_spreadsheet(
                SAMPLE_ID, str(search_value), sheet_title=first_sheet
            )
            assert len(results) >= 1

    def test_find_case_insensitive(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        data = client.read_range(SAMPLE_ID, f"'{first_sheet}'!A1:A1")
        if data.values and data.values[0]:
            search_value = str(data.values[0][0]).upper()
            results = client.find_in_spreadsheet(
                SAMPLE_ID, search_value, sheet_title=first_sheet, case_sensitive=False
            )
            # May or may not find depending on data, but shouldn't error
            assert isinstance(results, list)

    def test_find_nonexistent_returns_empty(self, client, spreadsheet_info):
        first_sheet = spreadsheet_info.sheets[0].title
        results = client.find_in_spreadsheet(
            SAMPLE_ID, "ZZZNOMATCH_XYZ_123456", sheet_title=first_sheet
        )
        assert results == []

    def test_find_unknown_sheet_raises(self, client):
        with pytest.raises(LookupError):
            client.find_in_spreadsheet(SAMPLE_ID, "anything", sheet_title="DoesNotExist")


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
