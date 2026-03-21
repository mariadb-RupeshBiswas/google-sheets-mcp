"""Pydantic models for Google Sheets MCP responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SheetProperties(BaseModel):
    """Properties of a single worksheet (tab) inside a spreadsheet."""

    sheet_id: int = Field(description="Numeric ID of the sheet")
    title: str = Field(description="Human-readable name of the sheet tab")
    index: int = Field(description="Zero-based position of the sheet among all tabs")
    sheet_type: str = Field(description="Sheet type, e.g. GRID, OBJECT, DATA_SOURCE")
    row_count: int = Field(description="Number of rows in the grid")
    column_count: int = Field(description="Number of columns in the grid")


class SpreadsheetInfo(BaseModel):
    """High-level metadata about a Google Spreadsheet."""

    spreadsheet_id: str = Field(description="Unique spreadsheet identifier")
    title: str = Field(description="Title shown in Google Drive")
    locale: str = Field(description="Locale setting for the spreadsheet")
    time_zone: str = Field(description="Time-zone for date/time cells")
    sheets: list[SheetProperties] = Field(description="All worksheets (tabs) in this spreadsheet")


class CellValue(BaseModel):
    """A single cell's value and location."""

    row: int = Field(description="1-based row index")
    column: int = Field(description="1-based column index")
    a1_notation: str = Field(description="A1 notation, e.g. 'B3'")
    value: Any = Field(default=None, description="The cell value (str, int, float, bool, or None)")


class RangeData(BaseModel):
    """Values read from an A1-notation range."""

    spreadsheet_id: str
    sheet_title: str
    range_notation: str = Field(description="Actual range returned by the API, e.g. Sheet1!A1:D10")
    row_count: int
    column_count: int
    values: list[list[Any]] = Field(
        description="2-D list of cell values; missing trailing cells are omitted by the API"
    )


class FindResult(BaseModel):
    """A cell that matched a search query."""

    sheet_title: str
    row: int = Field(description="1-based row index")
    column: int = Field(description="1-based column index")
    a1_notation: str
    matched_value: str
