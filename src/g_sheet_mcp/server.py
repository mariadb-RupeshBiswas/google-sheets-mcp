"""Google Sheets MCP Server.

Entry point for the MCP server.  Run via:
    uv run g-sheet-mcp            # stdio (Claude Desktop / any MCP client)
    uv run g-sheet-mcp --http     # streamable-HTTP on http://localhost:8000/mcp

Authentication (run once):
    gcloud auth login --enable-gdrive-access --update-adc
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from g_sheet_mcp.auth import AuthError, get_credentials
from g_sheet_mcp.sheets import SheetsClient, _client_lock, spreadsheet_id_from_url

logging.basicConfig(
    level=logging.WARNING,
    stream=sys.stderr,
    format="%(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="g-sheet-mcp",
    instructions=(
        "A read-only Google Sheets server.  "
        "All tools accept either a full Google Sheets URL or a bare spreadsheet ID.  "
        "Authentication uses Application Default Credentials – run "
        "`gcloud auth login --enable-gdrive-access --update-adc` once before use."
    ),
)


# ---------------------------------------------------------------------------
# Shared helper – lazy-initialised once per server lifetime
# ---------------------------------------------------------------------------

_client: SheetsClient | None = None


def _get_client() -> SheetsClient:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:  # double-checked locking
                try:
                    creds = get_credentials()
                except AuthError as exc:
                    logger.error("Authentication failed: %s", exc)
                    raise
                _client = SheetsClient(creds)
    return _client


def _resolve_id(spreadsheet_id_or_url: str) -> str:
    """Accept either a URL or a bare ID and return just the ID."""
    return spreadsheet_id_from_url(spreadsheet_id_or_url)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_spreadsheet_info(spreadsheet_id_or_url: str) -> dict[str, Any]:
    """Return metadata about a Google Spreadsheet: title, locale, timezone, and all sheet tabs.

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.

    Returns:
        Dictionary with spreadsheet metadata and list of worksheets.
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    info = _get_client().get_spreadsheet_info(sid)
    return info.model_dump()


@mcp.tool()
def list_sheets(spreadsheet_id_or_url: str) -> list[dict[str, Any]]:
    """List all worksheet tabs in a spreadsheet with their properties.

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.

    Returns:
        List of sheet property dicts (sheet_id, title, index, row_count, column_count).
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    info = _get_client().get_spreadsheet_info(sid)
    return [s.model_dump() for s in info.sheets]


@mcp.tool()
def read_range(
    spreadsheet_id_or_url: str,
    range_notation: str,
    value_render_option: str = "FORMATTED_VALUE",
) -> dict[str, Any]:
    """Read cell values from a specific A1-notation range.

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.
        range_notation: A1 range such as ``Sheet1!A1:D10`` or just ``A1:D10``.
            To target a named sheet use ``'My Sheet'!A:Z``.
        value_render_option: How values are rendered.
            - ``FORMATTED_VALUE`` (default): as displayed in the browser.
            - ``UNFORMATTED_VALUE``: raw numeric value.
            - ``FORMULA``: the formula text if a cell contains a formula.

    Returns:
        Dict with range metadata and ``values`` (2-D list of strings/numbers).
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    result = _get_client().read_range(
        spreadsheet_id=sid,
        range_notation=range_notation,
        value_render_option=value_render_option,
    )
    return result.model_dump()


@mcp.tool()
def read_sheet(
    spreadsheet_id_or_url: str,
    sheet_title: str,
    value_render_option: str = "FORMATTED_VALUE",
) -> dict[str, Any]:
    """Read all data from a named worksheet (tab).

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.
        sheet_title: Exact tab name, e.g. ``Sheet1`` or ``Budget 2025``.
        value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.

    Returns:
        Dict with sheet metadata and ``values`` (2-D list of cell values).
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    result = _get_client().read_sheet(
        spreadsheet_id=sid,
        sheet_title=sheet_title,
        value_render_option=value_render_option,
    )
    return result.model_dump()


@mcp.tool()
def get_cell(
    spreadsheet_id_or_url: str,
    sheet_title: str,
    row: int,
    column: int,
    value_render_option: str = "FORMATTED_VALUE",
) -> dict[str, Any]:
    """Read the value of a single cell by 1-based row and column index.

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.
        sheet_title: Exact tab name.
        row: 1-based row number (row 1 is the first row).
        column: 1-based column number (column 1 = A, 2 = B, …).
        value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.

    Returns:
        Dict with the cell's row, column, A1 notation, and value.
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    result = _get_client().get_cell(
        spreadsheet_id=sid,
        sheet_title=sheet_title,
        row=row,
        column=column,
        value_render_option=value_render_option,
    )
    return result.model_dump()


@mcp.tool()
def find_in_spreadsheet(
    spreadsheet_id_or_url: str,
    query: str,
    sheet_title: str = "",
    case_sensitive: bool = False,
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """Search all cells in a spreadsheet for a substring match.

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.
        query: Text to search for.
        sheet_title: If non-empty, restrict search to this sheet tab only.
        case_sensitive: Whether the match is case-sensitive (default False).
        max_results: Cap on the number of matching cells returned (default 50).

    Returns:
        List of matching cell dicts with sheet_title, row, column, a1_notation, matched_value.
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    results = _get_client().find_in_spreadsheet(
        spreadsheet_id=sid,
        query=query,
        sheet_title=sheet_title,
        case_sensitive=case_sensitive,
        max_results=max_results,
    )
    return [r.model_dump() for r in results]


@mcp.tool()
def read_sheet_as_records(
    spreadsheet_id_or_url: str,
    sheet_title: str,
    value_render_option: str = "FORMATTED_VALUE",
    max_rows: int = 1000,
) -> list[dict[str, Any]]:
    """Read a worksheet and return each row as a dict keyed by the header row.

    This is the most LLM-friendly format — instead of a 2-D array you get a
    list of named records that are easy to reason about.

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.
        sheet_title: Exact tab name.  The first row is treated as column headers.
        value_render_option: FORMATTED_VALUE (default), UNFORMATTED_VALUE, or FORMULA.
        max_rows: Safety cap on data rows returned (default 1000, max 10000).

    Returns:
        List of dicts ``[{"col_a": val, "col_b": val, ...}, ...]``.
        Missing cells in a row are represented as ``null``.
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    return _get_client().read_sheet_as_records(
        spreadsheet_id=sid,
        sheet_title=sheet_title,
        value_render_option=value_render_option,
        max_rows=min(max_rows, 10000),
    )


@mcp.tool()
def batch_read_ranges(
    spreadsheet_id_or_url: str,
    ranges: list[str],
    value_render_option: str = "FORMATTED_VALUE",
) -> list[dict[str, Any]]:
    """Read multiple A1-notation ranges in a single API call (efficient batching).

    Args:
        spreadsheet_id_or_url: Full Google Sheets URL *or* bare spreadsheet ID.
        ranges: List of A1 range strings, e.g. ``["Sheet1!A1:B5", "Sheet2!C1:C10"]``.
        value_render_option: FORMATTED_VALUE, UNFORMATTED_VALUE, or FORMULA.

    Returns:
        List of RangeData dicts in the same order as the input ranges.
    """
    sid = _resolve_id(spreadsheet_id_or_url)
    results = _get_client().batch_read_ranges(
        spreadsheet_id=sid,
        ranges=ranges,
        value_render_option=value_render_option,
    )
    return [r.model_dump() for r in results]


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------


@mcp.resource("spreadsheet://{spreadsheet_id}/info")
def spreadsheet_info_resource(spreadsheet_id: str) -> str:
    """Expose spreadsheet metadata as an MCP resource.

    URI: ``spreadsheet://<spreadsheet_id>/info``
    """
    info = _get_client().get_spreadsheet_info(spreadsheet_id)
    lines = [
        f"Title: {info.title}",
        f"Spreadsheet ID: {info.spreadsheet_id}",
        f"Locale: {info.locale}",
        f"Timezone: {info.time_zone}",
        "",
        "Sheets:",
    ]
    for s in info.sheets:
        lines.append(f"  [{s.index}] {s.title!r}  ({s.row_count} rows × {s.column_count} cols)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Sheets MCP Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run with Streamable-HTTP transport instead of stdio (default).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP transport (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        mcp.settings.log_level = "DEBUG"

    if args.http:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
