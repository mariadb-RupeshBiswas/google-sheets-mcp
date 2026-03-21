# Example Interactions — Google Sheets MCP

Real examples of how an agent should use the google-sheets MCP tools.

---

## Example 1: Discover and read a spreadsheet

**User:** "What's in this spreadsheet? https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit"

**Agent flow:**

```python
# Step 1: discover the spreadsheet
info = get_spreadsheet_info("https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit")
# → title: "Example Spreadsheet", tabs: ["Example Sheet 1", ..., "Example Sheet 8"]

# Step 2: read the first tab as records
records = read_sheet_as_records(
    "https://docs.google.com/spreadsheets/d/EXAMPLE_SPREADSHEET_ID/edit",
    "Example Sheet 1",
    max_rows=5
)
# → [{"example_id": "OP-001", "example_name": "Deal A", ...}, ...]
```

**Agent response:** "This spreadsheet is called 'Example Spreadsheet' and has 8 tabs (Example Sheet 1–8). Each tab has 53 columns including example_id, example_name, opp_stage, example_value_usd, and more sales opportunity data."

---

## Example 2: Read a specific range

**User:** "Show me columns A to D from Example Sheet 2"

```python
data = read_range(
    "EXAMPLE_SPREADSHEET_ID",
    "'Example Sheet 2'!A1:D10"
)
# → values: [["example_id", "example_name", "opp_type", "opp_stage"], ["OP-001", ...], ...]
```

---

## Example 3: Search for a value

**User:** "Find all cells containing 'Closed Won' in Example Sheet 1"

```python
results = find_in_spreadsheet(
    "EXAMPLE_SPREADSHEET_ID",
    "Closed Won",
    sheet_title="Example Sheet 1",
    case_sensitive=False
)
# → [{"sheet_title": "Example Sheet 1", "row": 2, "column": 4, "a1_notation": "D2", "matched_value": "Closed Won"}]
```

---

## Example 4: Read headers from all 8 tabs efficiently

**User:** "Do all 8 test case tabs have the same column headers?"

```python
# One batch call instead of 8 separate calls
results = batch_read_ranges(
    "EXAMPLE_SPREADSHEET_ID",
    [
        "'Example Sheet 1'!A1:AZ1",
        "'Example Sheet 2'!A1:AZ1",
        "'Example Sheet 3'!A1:AZ1",
        "'Example Sheet 4'!A1:AZ1",
        "'Example Sheet 5'!A1:AZ1",
        "'Example Sheet 6'!A1:AZ1",
        "'Example Sheet 7'!A1:AZ1",
        "'Example Sheet 8'!A1:AZ1",
    ]
)
# Compare results[0].values[0] == results[1].values[0] == ... etc
```

---

## Example 5: Get a specific cell

**User:** "What is the value in row 2 column 3 of Example Sheet 1?"

```python
cell = get_cell(
    "EXAMPLE_SPREADSHEET_ID",
    "Example Sheet 1",
    row=2,
    column=3
)
# → {"row": 2, "column": 3, "a1_notation": "C2", "value": "New Business"}
```

---

## Example 6: Read raw formulas

**User:** "What formula is in cell E2?"

```python
cell = get_cell(
    "EXAMPLE_SPREADSHEET_ID",
    "Example Sheet 1",
    row=2,
    column=5,
    value_render_option="FORMULA"
)
# → {"value": "=IF(D2=\"Closed Won\",B2*0.9,B2)"}
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
    # → "I couldn't find a 'Summary' tab. Available tabs are: Example Sheet 1, ..., Example Sheet 8"
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
closed_won = [r for r in records if r.get("opp_stage") == "Closed Won"]

# 4. Present
"Found 3 Closed Won opportunities: ..."
```

### Pattern: Multi-tab summary

```python
# Read header row from all tabs at once
ranges = [f"'{s.title}'!A1:A1" for s in info.sheets]
headers = batch_read_ranges(url, ranges)
# Check if all tabs share the same schema
```
