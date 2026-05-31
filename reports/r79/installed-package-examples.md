# R79 Train K — Installed Package Examples

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** K

## FODS Installed Package Usage Examples

After installing the wheel with:
```bash
pip install aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl
```

### Example 1: Parse a FODS file
```python
import fods

# Parse
doc = fods.parse_fods("my-spreadsheet.fods")

# Inspect sheets
sheets = fods.workbook_sheet_order(doc)
print(f"Sheets: {sheets}")

# Get stats
stats = fods.workbook_stats(doc)
print(f"Stats: {stats}")
```

### Example 2: Sheet Management (R77 APIs)
```python
import fods

doc = fods.parse_fods("my-spreadsheet.fods")

# Add a new sheet
ok, msg = fods.workbook_add_sheet(doc, "NewSheet")
assert ok, msg

# Rename a sheet
ok, msg = fods.workbook_rename_sheet(doc, "Sheet1", "MainData")
assert ok, msg

# Write back
fods.write_fods(doc, "updated-spreadsheet.fods")
```

### Example 3: Cell Operations
```python
import fods

doc = fods.parse_fods("my-spreadsheet.fods")

# Set cell value
ok, msg = fods.workbook_set_cell_value(doc, "Sheet1", 0, 0, "Hello World")
assert ok, msg

# Write
fods.write_fods(doc, "output.fods")
```

## FODT Installed Package Usage Examples

After installing:
```bash
pip install aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl
```

### Example 1: Parse and Inspect
```python
import fodt

doc = fodt.parse_fodt("my-document.fodt")

text = fodt.document_text_content(doc)
outline = fodt.document_heading_outline(doc)
count = fodt.document_paragraph_count(doc)
print(f"Words: {fodt.document_word_count(doc)}")
```

### Example 2: Paragraph Management (R77 APIs, R79-fixed)
```python
import fodt

doc = fodt.parse_fodt("my-document.fodt")

# Count before
count_before = fodt.document_paragraph_count(doc)

# Append new paragraph (R79: now survives write/parse roundtrip)
ok, msg = fodt.document_append_paragraph(doc, "New conclusion paragraph.")
assert ok, msg

# Write
fodt.write_fodt(doc, "updated-document.fodt")

# Verify roundtrip
doc2 = fodt.parse_fodt("updated-document.fodt")
count_after = fodt.document_paragraph_count(doc2)
assert count_after == count_before + 1  # PASSES after R79 GAP fix
```

## Import Namespace Summary

| Package | Installed import | Wrong (fails) |
|---|---|---|
| FODS | `import fods` | `import aspose_format_factory_fods` |
| FODT | `import fodt` | `import aspose_format_factory_fodt` |
| ZST | `import zst` | `import aspose_format_factory_zst` |

TRAIN_K_STATUS: COMPLETE
