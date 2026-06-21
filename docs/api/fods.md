# FODS Python API Reference

**Package:** `aspose-format-factory-fods`
**Version:** 0.1.0
**Format:** Flat OpenDocument Spreadsheet (FODS)
**Spec:** OASIS ODF 1.3

---

## Installation

```bash
pip install aspose-format-factory-fods
```

```python
import fods
```

---

## Core Functions

### `parse_fods`

```python
def parse_fods(file_path: str | os.PathLike) -> dict[str, Any]
```

Parse a FODS file and return a workbook dictionary.

**Parameters:**
- `file_path` — Path to the `.fods` file

**Returns:** Workbook dict with keys: `sheets` (list), `styles` (dict), `named_ranges` (list), `odf_version` (str)

**Raises:** `FodsInputError` if file not found; `FodsParseError` if XML is malformed; `FodsSizeError` if file exceeds `MAX_FILE_BYTES`

**Example:**
```python
doc = fods.parse_fods("budget.fods")
print(doc["odf_version"])  # "1.3"
print(len(doc["sheets"]))  # number of sheets
```

---

### `parse_fods_strict`

```python
def parse_fods_strict(file_path: str | os.PathLike) -> dict[str, Any]
```

Parse a FODS file with strict validation. Raises on any structural warning that `parse_fods` would tolerate.

**Parameters:** Same as `parse_fods`

**Returns:** Same as `parse_fods`

**Raises:** Same as `parse_fods`, plus `FodsParseError` on structural warnings

---

### `write_fods`

```python
def write_fods(workbook: dict[str, Any], file_path: str | Path) -> None
```

Write a workbook dictionary to a FODS file.

**Parameters:**
- `workbook` — Workbook dict (as returned by `parse_fods` or built with `build_workbook`)
- `file_path` — Output path for the `.fods` file

**Example:**
```python
doc = fods.parse_fods("input.fods")
fods.workbook_set_cell_value(doc, "Sheet1", 0, 0, "Hello")
fods.write_fods(doc, "output.fods")
```

---

### `workbook_to_xml`

```python
def workbook_to_xml(workbook: dict[str, Any]) -> str
```

Serialize a workbook dict to ODF XML string without writing to disk.

**Returns:** XML string (UTF-8 encoded FODS content)

---

## Cell Access and Modification

### `workbook_get_cell_value`

```python
def workbook_get_cell_value(
    workbook: dict[str, Any],
    sheet_name: str,
    row_index: int,
    col_index: int,
) -> Any
```

Get the value of a cell by sheet name and zero-based row/column indices.

**Returns:** Cell value (str, int, float, or None)

---

### `workbook_set_cell_value`

```python
def workbook_set_cell_value(
    workbook: dict[str, Any],
    sheet_name: str,
    row_idx: int,
    col_idx: int,
    value: Any,
    value_type: str | None = None,
) -> tuple[bool, str]
```

Set the value of a cell. Returns `(success: bool, message: str)`.

**Parameters:**
- `value_type` — Optional ODF value type: `"string"`, `"float"`, `"boolean"`, `"date"`, `"time"`

---

### `workbook_cell_text_at`

```python
def workbook_cell_text_at(workbook: dict[str, Any], sheet_name: str, row_index: int, col_index: int) -> str
```

Get the display text of a cell (as shown to the user, not raw value).

---

### `workbook_find_cells`

```python
def workbook_find_cells(workbook: dict[str, Any]) -> list[dict]
```

Return a list of all non-empty cells across all sheets.

---

### `workbook_count_matching_cells`

```python
def workbook_count_matching_cells(workbook: dict[str, Any]) -> int
```

Count cells matching a filter criterion.

---

## Sheet Operations

### `find_sheet_by_name`

```python
def find_sheet_by_name(workbook: dict[str, Any], name: str) -> dict[str, Any] | None
```

Find a sheet by name. Returns the sheet dict or `None` if not found.

---

### `workbook_add_sheet`

```python
def workbook_add_sheet(
    workbook: dict[str, Any],
    sheet_name: str,
    position: int | None = None,
) -> tuple[bool, str]
```

Add a new sheet. Returns `(success, message)`. Fails if name already exists.

---

### `workbook_rename_sheet`

```python
def workbook_rename_sheet(
    workbook: dict[str, Any],
    old_name: str,
    new_name: str,
) -> tuple[bool, str]
```

Rename an existing sheet. Returns `(success, message)`.

---

### `workbook_remove_sheet`

```python
def workbook_remove_sheet(
    workbook: dict[str, Any],
    sheet_name: str,
) -> tuple[bool, str]
```

Remove a sheet by name. Returns `(success, message)`.

---

## Export

### `workbook_to_csv`

```python
def workbook_to_csv(
    workbook: dict[str, Any],
    sheet_name: str | None = None,
) -> str
```

Export workbook to CSV string. If `sheet_name` is None, exports the first sheet.

**Example:**
```python
doc = fods.parse_fods("data.fods")
csv_text = fods.workbook_to_csv(doc, sheet_name="Sales")
with open("sales.csv", "w") as f:
    f.write(csv_text)
```

---

### `workbook_to_html`

```python
def workbook_to_html(workbook: dict[str, Any]) -> str
```

Export workbook to an HTML table string.

---

## Analytics Functions

### `fods_sheet_count`

```python
def fods_sheet_count(workbook: dict[str, Any]) -> int
```

Return the number of sheets in the workbook.

---

### `fods_total_cell_count`

```python
def fods_total_cell_count(workbook: dict[str, Any]) -> int
```

Return the total number of cells across all sheets (including empty cells).

---

### `fods_empty_cell_count`

```python
def fods_empty_cell_count(workbook: dict[str, Any]) -> int
```

Return the count of empty cells across all sheets.

---

### `fods_has_formulas`

```python
def fods_has_formulas(workbook: dict[str, Any]) -> bool
```

Return True if any sheet contains formula cells.

---

### `fods_sheet_names`

```python
def fods_sheet_names(workbook: dict[str, Any]) -> list[str]
```

Return a list of sheet names in document order.

---

### `workbook_stats`

```python
def workbook_stats(workbook: dict[str, Any]) -> dict[str, Any]
```

Return a statistics summary dict: sheet count, total cells, numeric count, string count, formula count, empty count.

---

### `workbook_row_count`

```python
def workbook_row_count(workbook: dict[str, Any]) -> int
```

Return total number of data rows across all sheets.

---

### `workbook_column_count`

```python
def workbook_column_count(workbook: dict[str, Any]) -> int
```

Return maximum column count across all sheets.

---

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `FORMAT_ID` | `"FODS"` | Format identifier |
| `SPEC_VERSION` | `"1.3"` | ODF spec version supported |
| `PACKAGE_VERSION` | `"0.1.0"` | Package version |
| `MAX_FILE_BYTES` | `104857600` | File size limit (100 MB) |

---

## Exception Classes

| Class | Description |
|-------|-------------|
| `FodsError` | Base exception |
| `FodsInputError` | File not found or unreadable |
| `FodsSizeError` | File exceeds `MAX_FILE_BYTES` |
| `FodsParseError` | XML parse error or invalid FODS structure |

---

## Quick Start

```python
import fods

# Load a FODS file
doc = fods.parse_fods("budget.fods")

# Inspect
print(fods.fods_sheet_names(doc))       # ["Sheet1", "Summary"]
print(fods.fods_sheet_count(doc))       # 2
print(fods.fods_total_cell_count(doc))  # 128

# Read a cell
value = fods.workbook_get_cell_value(doc, "Sheet1", 0, 0)

# Edit a cell
fods.workbook_set_cell_value(doc, "Sheet1", 0, 0, "Updated", value_type="string")

# Save
fods.write_fods(doc, "budget_updated.fods")

# Export to CSV
csv = fods.workbook_to_csv(doc, sheet_name="Sheet1")
```
