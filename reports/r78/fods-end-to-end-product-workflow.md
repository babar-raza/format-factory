# R78 FODS End-to-End Product Workflow

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** E

## Workflow Definition

The FODS product end-to-end workflow proves that a consumer can:
1. Parse a FODS file into the neutral model
2. Inspect it using analysis APIs
3. Edit cells and manage sheets
4. Write to a new FODS file
5. Verify the round-trip is correct
6. Export to CSV

## Workflow Proof

All steps verified via `tests/python/fods/test_r78_fods_end_to_end_workflow.py` (50 tests total, 15 from this file).

### Step 1: Parse

```python
from src.python.fods import parse_fods
wb = parse_fods("minimal-spreadsheet.fods")
# Returns: {"sheets": [...], ...}
```
TEST_COVERAGE: test_parse_returns_workbook — PASS

### Step 2: Inspect

```python
stats = workbook_stats(wb)
sheets = workbook_sheet_order(wb)
summary = workbook_sheet_summary(wb)
```
TEST_COVERAGE: TestFodsParseAndInspect — 5 tests, all PASS

### Step 3: Edit

```python
ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 0, "Updated Value")
# Note: set_cell_value requires existing row — returns False on empty row
```
TEST_COVERAGE: test_set_cell_value_and_round_trip — PASS

### Step 4: Sheet Management

```python
ok, _ = workbook_add_sheet(wb, "Summary", position=-1)
ok, _ = workbook_rename_sheet(wb, "Summary", "Q4_Summary")
ok, _ = workbook_remove_sheet(wb, "Q4_Summary")
```
TEST_COVERAGE: TestFodsSheetManagementWorkflow — 3 tests, all PASS

### Step 5: Write + Round-trip

```python
write_fods(wb, "output.fods")
wb2 = parse_fods("output.fods")
assert workbook_sheet_order(wb2) == workbook_sheet_order(wb)
```
TEST_COVERAGE: test_multi_sheet_write_round_trip — PASS

### Step 6: CSV Export

```python
from src.python.fods.csv_exporter import export_fods_to_csv_file
export_fods_to_csv_file(wb, "output.csv", sheet_index=0)
```
TEST_COVERAGE: TestFodsCsvExportWorkflow — 2 tests, all PASS

## Example File

`examples/python/fods/edit_save_export_fods.py` — demonstrates complete workflow:
- Load → inspect → edit cell → add sheet → save FODS → export CSV → verify round-trip

## Known Workflow Limitations

1. `workbook_set_cell_value` requires existing row — cannot create new rows
2. Sheet management (add_sheet) creates empty sheets — cannot populate in one call
3. CSV export uses `sheet_index` (not sheet name) — caller must resolve name→index
4. No column/row insertion API — only cell value editing

FODS_END_TO_END_WORKFLOW: VERIFIED
NEW_TESTS: 15 (tests/python/fods/test_r78_fods_end_to_end_workflow.py)
NEW_EXAMPLES: 1 (examples/python/fods/edit_save_export_fods.py)
