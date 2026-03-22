# 💬 Example Interactions — Google Sheets MCP

Sanitized examples of how an agent should use the google-sheets MCP tools.

All spreadsheet IDs and values below are placeholders for public documentation.

---

## Example 1: Discover and read a spreadsheet

**User:** "What's in this spreadsheet? https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit"

**Agent flow:**

```python
# Step 1: discover the spreadsheet
info = get_spreadsheet_info("https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit")
# → title: "My Data", tabs: ["Sheet1", "Sheet2", "Sheet3"]

# Step 2: read the first tab as records
records = read_sheet_as_records(
    "https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit",
    "Sheet1",
    max_rows=5
)
# → [{"id": "001", "name": "Item A", "value": "100"}, ...]
```

**Agent response:** "This spreadsheet is called 'My Data' and has 3 tabs. Sheet1 contains records with columns like id, name, and value."

---

## Example 2: Read a specific range

**User:** "Show me columns A to D from Sheet2"

```python
data = read_range(
    "EXAMPLE_SPREADSHEET_ID",
    "'Sheet2'!A1:D10"
)
# → values: [["id", "name", "category", "status"], ["001", "Item A", "Type1", "Active"], ...]
```

---

## Example 3: Search for a value

**User:** "Find all cells containing 'Complete' in Sheet1"

```python
results = find_in_spreadsheet(
    "EXAMPLE_SPREADSHEET_ID",
    "Complete",
    sheet_title="Sheet1",
    case_sensitive=False
)
# → [{"sheet_title": "Sheet1", "row": 2, "column": 4, "a1_notation": "D2", "matched_value": "Complete"}]
```

---

## Example 4: Read headers from multiple tabs efficiently

**User:** "Do all my sheets have the same column headers?"

```python
# One batch call instead of multiple separate calls
results = batch_read_ranges(
    "EXAMPLE_SPREADSHEET_ID",
    [
        "'Sheet1'!A1:Z1",
        "'Sheet2'!A1:Z1",
        "'Sheet3'!A1:Z1",
    ]
)
# Compare results[0].values[0] == results[1].values[0] == ... etc
```

---

## Example 5: Get a specific cell

**User:** "What is the value in row 2 column 3 of Sheet1?"

```python
cell = get_cell(
    "EXAMPLE_SPREADSHEET_ID",
    "Sheet1",
    row=2,
    column=3
)
# → {"row": 2, "column": 3, "a1_notation": "C2", "value": "Category A"}
```

---

## Example 6: Read raw formulas

**User:** "What formula is in cell E2?"

```python
cell = get_cell(
    "EXAMPLE_SPREADSHEET_ID",
    "Sheet1",
    row=2,
    column=5,
    value_render_option="FORMULA"
)
# → {"value": "=IF(D2=\"Complete\",B2*0.9,B2)"}
```

---

## Example 7: Handle sheet not found

**User:** "Read the 'Summary' tab"

```python
# Attempt read
try:
    records = read_sheet_as_records(spreadsheet_id, "Summary")
except LookupError:
    # Fall back: show available tabs
    sheets = list_sheets(spreadsheet_id)
    # → "I couldn't find a 'Summary' tab. Available tabs are: Sheet1, Sheet2, Sheet3"
```

---

## Common patterns

### Pattern: Explore → Filter → Present

```python
# 1. Discover
info = get_spreadsheet_info(url)

# 2. Read the relevant tab
records = read_sheet_as_records(url, info.sheets[0].title)

# 3. Filter in-memory (Python/agent logic)
completed = [r for r in records if r.get("status") == "Complete"]

# 4. Present
"Found 3 completed items: ..."
```

### Pattern: Multi-tab summary

```python
# Read header row from all tabs at once
ranges = [f"'{s.title}'!A1:A1" for s in info.sheets]
headers = batch_read_ranges(url, ranges)
# Check if all tabs share the same schema
```
