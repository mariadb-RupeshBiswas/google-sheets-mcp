"""Google Sheets API v4 wrapper (read-only).

All methods are synchronous because the Sheets REST API is called via
google-api-python-client, which uses httplib2 under the hood.  FastMCP
wraps calls in a thread pool automatically when tools are not async.
"""

from __future__ import annotations

import logging
import re
import threading
from typing import Any, NoReturn

import google.auth.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from g_sheet_mcp.models import (
    CellValue,
    FindResult,
    RangeData,
    SheetProperties,
    SpreadsheetInfo,
)

logger = logging.getLogger(__name__)

_SPREADSHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9_-]+)")

_VALID_RENDER_OPTIONS = frozenset({"FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"})

_client_lock = threading.Lock()


def _col_to_letter(col: int) -> str:
    """Convert a 1-based column index to A1-notation letters (e.g. 1 → A, 27 → AA)."""
    result = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _a1(row: int, col: int) -> str:
    """Return A1 notation for a 1-based (row, col) pair."""
    return f"{_col_to_letter(col)}{row}"


def _quote_sheet(title: str) -> str:
    """Wrap a sheet title in single quotes for use in A1 range notation.

    The Sheets API requires ``'Sheet Name'!A1:Z10`` when the title contains
    spaces or special characters.  Single quotes inside the title are escaped
    by doubling them (``''``).
    """
    escaped = title.replace("'", "''")
    return f"'{escaped}'"


def _validate_render_option(option: str) -> None:
    """Raise ValueError for unknown valueRenderOption strings."""
    if option not in _VALID_RENDER_OPTIONS:
        raise ValueError(
            f"Invalid value_render_option {option!r}. "
            f"Must be one of: {', '.join(sorted(_VALID_RENDER_OPTIONS))}"
        )


def spreadsheet_id_from_url(url: str) -> str:
    """Extract the spreadsheet ID from a full Google Sheets URL.

    Args:
        url: A Google Sheets URL such as
             https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0

    Returns:
        The extracted spreadsheet ID string.

    Raises:
        ValueError: If the URL does not contain a recognisable spreadsheet ID.
    """
    match = _SPREADSHEET_ID_RE.search(url)
    if match:
        return match.group(1)
    if re.match(r"^[a-zA-Z0-9_-]{20,}$", url):
        return url
    raise ValueError(
        f"Cannot extract a spreadsheet ID from: {url!r}\n"
        "Pass either a full Google Sheets URL or a bare spreadsheet ID."
    )


class SheetsClient:
    """Thin read-only wrapper around the Google Sheets API v4."""

    def __init__(self, credentials: google.auth.credentials.Credentials) -> None:
        self._service = build(
            "sheets",
            "v4",
            credentials=credentials,
            cache_discovery=False,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_spreadsheet_info(self, spreadsheet_id: str) -> SpreadsheetInfo:
        """Fetch metadata for a spreadsheet.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.

        Returns:
            SpreadsheetInfo with title, locale, timezone, and all sheet tabs.

        Raises:
            ValueError: If spreadsheet_id is empty or whitespace.
            PermissionError: If user lacks read access (HTTP 403).
            FileNotFoundError: If spreadsheet does not exist (HTTP 404).
        """
        if not spreadsheet_id or not spreadsheet_id.strip():
            raise ValueError("spreadsheet_id must be a non-empty string.")
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        try:
            result = (
                self._service.spreadsheets()
                .get(
                    spreadsheetId=spreadsheet_id,
                    includeGridData=False,
                )
                .execute()
            )
        except HttpError as exc:
            _raise_friendly(exc, spreadsheet_id)

        props = result.get("properties", {})
        sheets_raw = result.get("sheets", [])

        sheets = [
            SheetProperties(
                sheet_id=s["properties"].get("sheetId", 0),
                title=s["properties"].get("title", ""),
                index=s["properties"].get("index", 0),
                sheet_type=s["properties"].get("sheetType", "GRID"),
                row_count=s["properties"].get("gridProperties", {}).get("rowCount", 0),
                column_count=s["properties"].get("gridProperties", {}).get("columnCount", 0),
            )
            for s in sheets_raw
        ]

        return SpreadsheetInfo(
            spreadsheet_id=spreadsheet_id,
            title=props.get("title", ""),
            locale=props.get("locale", ""),
            time_zone=props.get("timeZone", ""),
            sheets=sheets,
        )

    def read_range(
        self,
        spreadsheet_id: str,
        range_notation: str,
        value_render_option: str = "FORMATTED_VALUE",
    ) -> RangeData:
        """Read values from an A1-notation range.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.
            range_notation: A1 notation such as ``Sheet1!A1:D10`` or just ``A1:D10``.
            value_render_option: One of FORMATTED_VALUE (default), UNFORMATTED_VALUE,
                or FORMULA.

        Returns:
            RangeData containing the 2-D list of cell values.
        """
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        if not range_notation or not range_notation.strip():
            raise ValueError("range_notation must be a non-empty string.")
        _validate_render_option(value_render_option)
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation,
                    valueRenderOption=value_render_option,
                )
                .execute()
            )
        except HttpError as exc:
            _raise_friendly(exc, spreadsheet_id)

        actual_range = result.get("range", range_notation)
        values: list[list[Any]] = result.get("values", [])

        sheet_title = actual_range.split("!")[0].strip("'") if "!" in actual_range else ""
        row_count = len(values)
        col_count = max((len(r) for r in values), default=0)

        return RangeData(
            spreadsheet_id=spreadsheet_id,
            sheet_title=sheet_title,
            range_notation=actual_range,
            row_count=row_count,
            column_count=col_count,
            values=values,
        )

    def read_sheet(
        self,
        spreadsheet_id: str,
        sheet_title: str,
        value_render_option: str = "FORMATTED_VALUE",
    ) -> RangeData:
        """Read all data from a named worksheet.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.
            sheet_title: The exact tab name (case-sensitive).  Sheet names
                containing spaces or special characters are quoted automatically.
            value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.

        Returns:
            RangeData for the entire sheet content.
        """
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        if not sheet_title or not sheet_title.strip():
            raise ValueError("sheet_title must be a non-empty string.")
        return self.read_range(
            spreadsheet_id=spreadsheet_id,
            range_notation=_quote_sheet(sheet_title),
            value_render_option=value_render_option,
        )

    def get_cell(
        self,
        spreadsheet_id: str,
        sheet_title: str,
        row: int,
        column: int,
        value_render_option: str = "FORMATTED_VALUE",
    ) -> CellValue:
        """Read a single cell by 1-based row/column indices.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.
            sheet_title: The exact worksheet tab name.
            row: 1-based row number (row 1 is the first row).
            column: 1-based column number (1=A, 2=B, ...).
            value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.

        Returns:
            CellValue with row, column, a1_notation, and value.

        Raises:
            ValueError: If row or column is < 1.
        """
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        if row < 1:
            raise ValueError(f"row must be >= 1, got {row}.")
        if column < 1:
            raise ValueError(f"column must be >= 1, got {column}.")
        notation = _a1(row, column)
        full_range = f"{_quote_sheet(sheet_title)}!{notation}"
        result = self.read_range(
            spreadsheet_id=spreadsheet_id,
            range_notation=full_range,
            value_render_option=value_render_option,
        )
        value = result.values[0][0] if result.values and result.values[0] else None
        return CellValue(
            row=row,
            column=column,
            a1_notation=notation,
            value=value,
        )

    def find_in_spreadsheet(
        self,
        spreadsheet_id: str,
        query: str,
        sheet_title: str = "",
        case_sensitive: bool = False,
        max_results: int = 50,
    ) -> list[FindResult]:
        """Search for a substring across all or one sheet.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.
            query: The text to search for.
            sheet_title: If provided, search only this tab. Otherwise search all sheets.
            case_sensitive: Whether to match case exactly (default False).
            max_results: Stop after finding this many matches.

        Returns:
            List of FindResult objects with sheet_title, row, column, a1_notation, matched_value.

        Raises:
            ValueError: If query is empty or max_results <= 0.
            LookupError: If sheet_title is specified but does not exist.
        """
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string.")
        if max_results <= 0:
            raise ValueError(f"max_results must be > 0, got {max_results}.")
        max_results = min(max_results, 500)

        info = self.get_spreadsheet_info(spreadsheet_id)
        if sheet_title:
            target_sheets = [s for s in info.sheets if s.title == sheet_title]
            if not target_sheets:
                available = ", ".join(f"'{s.title}'" for s in info.sheets)
                raise LookupError(
                    f"Sheet '{sheet_title}' not found in spreadsheet '{spreadsheet_id}'. "
                    f"Available sheets: {available}"
                )
        else:
            target_sheets = list(info.sheets)

        matches: list[FindResult] = []
        needle = query if case_sensitive else query.lower()

        for sheet in target_sheets:
            data = self.read_sheet(
                spreadsheet_id=spreadsheet_id,
                sheet_title=sheet.title,
            )
            for r_idx, row in enumerate(data.values, start=1):
                for c_idx, cell in enumerate(row, start=1):
                    cell_str = str(cell)
                    haystack = cell_str if case_sensitive else cell_str.lower()
                    if needle in haystack:
                        matches.append(
                            FindResult(
                                sheet_title=sheet.title,
                                row=r_idx,
                                column=c_idx,
                                a1_notation=_a1(r_idx, c_idx),
                                matched_value=cell_str,
                            )
                        )
                        if len(matches) >= max_results:
                            return matches
        return matches

    def read_sheet_as_records(
        self,
        spreadsheet_id: str,
        sheet_title: str,
        value_render_option: str = "FORMATTED_VALUE",
        max_rows: int = 1000,
    ) -> list[dict[str, Any]]:
        """Read worksheet data as a list of dicts (first row = headers).

        This is the most LLM-friendly format for tabular data.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.
            sheet_title: The exact tab name.
            value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.
            max_rows: Maximum number of data rows to return (excludes header row).

        Returns:
            List of dicts where each dict is one data row, keyed by the header.
            Missing cells in a row are represented as None.

        Raises:
            ValueError: If max_rows <= 0.
        """
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        if max_rows <= 0:
            raise ValueError(f"max_rows must be > 0, got {max_rows}.")
        data = self.read_sheet(
            spreadsheet_id=spreadsheet_id,
            sheet_title=sheet_title,
            value_render_option=value_render_option,
        )
        if not data.values:
            return []
        headers = [str(h) for h in data.values[0]]
        records: list[dict[str, Any]] = []
        for raw_row in data.values[1 : max_rows + 1]:
            record: dict[str, Any] = {}
            for i, header in enumerate(headers):
                record[header] = raw_row[i] if i < len(raw_row) else None
            records.append(record)
        return records

    def batch_read_ranges(
        self,
        spreadsheet_id: str,
        ranges: list[str],
        value_render_option: str = "FORMATTED_VALUE",
    ) -> list[RangeData]:
        """Read multiple ranges in a single API call.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID or full URL.
            ranges: List of A1 range notations (e.g. ["Sheet1!A1:B5", "Sheet2!C1:C10"]).
            value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.

        Returns:
            List of RangeData, one per input range (same order).

        Raises:
            ValueError: If ranges is empty.
        """
        spreadsheet_id = spreadsheet_id_from_url(spreadsheet_id)
        if not ranges:
            raise ValueError("ranges must contain at least one range notation.")
        _validate_render_option(value_render_option)
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .batchGet(
                    spreadsheetId=spreadsheet_id,
                    ranges=ranges,
                    valueRenderOption=value_render_option,
                )
                .execute()
            )
        except HttpError as exc:
            _raise_friendly(exc, spreadsheet_id)

        output: list[RangeData] = []
        for vr in result.get("valueRanges", []):
            actual_range = vr.get("range", "")
            values = vr.get("values", [])
            sheet_title = actual_range.split("!")[0].strip("'") if "!" in actual_range else ""
            output.append(
                RangeData(
                    spreadsheet_id=spreadsheet_id,
                    sheet_title=sheet_title,
                    range_notation=actual_range,
                    row_count=len(values),
                    column_count=max((len(r) for r in values), default=0),
                    values=values,
                )
            )
        return output


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _raise_friendly(exc: HttpError, spreadsheet_id: str) -> NoReturn:
    """Re-raise HttpError with a human-friendly message."""
    status = exc.resp.status
    if status == 403:
        raise PermissionError(
            f"Access denied to spreadsheet '{spreadsheet_id}'.\n"
            "Make sure:\n"
            "  1. You ran: gcloud auth login --enable-gdrive-access --update-adc\n"
            "  2. Your Google account has at least Viewer access to the spreadsheet."
        ) from exc
    if status == 404:
        raise FileNotFoundError(
            f"Spreadsheet '{spreadsheet_id}' not found. "
            "Check the ID and that your account has access."
        ) from exc
    if status == 429:
        raise RuntimeError(
            "Google Sheets API rate limit exceeded. Wait a moment and try again."
        ) from exc
    if status >= 500:
        raise RuntimeError(
            f"Google Sheets API server error (HTTP {status}). Try again later."
        ) from exc
    raise exc
