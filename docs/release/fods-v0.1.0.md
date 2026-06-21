# FODS Release Notes — v0.1.0

**Package:** `aspose-format-factory-fods`
**Version:** 0.1.0
**Release Date:** 2026-06-21
**Track:** Python FOSS
**Format:** Flat OpenDocument Spreadsheet (OASIS ODF 1.3)

---

## Summary

First pre-release of the Format Factory FODS Python package.
Provides parse, inspect, edit, and export capabilities for `.fods` files.

This is a `v0.1.0` developer release. Not yet published to PyPI.
Commercial .NET product is separately tracked under `aspose-format-factory-fods` NuGet.

---

## Features

### Parse
- `parse_fods(path)` — Load a FODS file into a workbook dict (dict-based API)
- `parse_fods_strict(path)` — Strict mode with structural validation
- ODF 1.3 compliant XML parsing via stdlib `xml.etree.ElementTree` with security hardening
- File size guard: configurable via `MAX_FILE_BYTES` (default 100 MB)
- DTD prohibition enforced via `XmlResolver = null` equivalent

### Write
- `write_fods(workbook, path)` — Serialize workbook dict to `.fods` XML
- `workbook_to_xml(workbook)` — In-memory XML serialization

### Cell Access and Editing
- `workbook_get_cell_value` — Read cell by sheet + zero-based row/col indices
- `workbook_set_cell_value` — Write cell with optional ODF value type
- `workbook_cell_text_at` — Get display text of a cell

### Sheet Operations
- `find_sheet_by_name`, `workbook_add_sheet`, `workbook_rename_sheet`, `workbook_remove_sheet`
- Mutation operations return `(success: bool, message: str)` tuples

### Export
- `workbook_to_csv` — Per-sheet or full-workbook CSV export
- `workbook_to_html` — HTML table export

### Analytics (85 total public functions)
- `fods_sheet_count`, `fods_total_cell_count`, `fods_empty_cell_count`, `fods_has_formulas`, `fods_sheet_names`
- `workbook_stats` — Aggregate statistics dict
- `workbook_row_count`, `workbook_column_count`, `workbook_numeric_density`, `workbook_total_numeric_value`
- Full list: see `docs/api/fods.md`

---

## Test Evidence

| Suite | Count | Status |
|-------|-------|--------|
| Python FOSS core (52 tests) | 52/52 | PASS |
| .NET commercial (617 tests) | 617/617 | PASS |
| Install proof (Sprint R128) | Wheel + import + API smoke | PASS |

---

## Known Limitations

1. **Dict-based API** — Workbook model is a plain Python dict, not a class-based object model.
   Class-based migration is planned for a future release (P1 criterion from spec-to-feature plan).

2. **No PDF/PNG export** — Python track does not include PDF or PNG rendering.
   PDF rendering is available in the .NET commercial product only.

3. **Analytics functions are pre-release** — ~60 analytics functions (fods_*) are functional
   but not formally spec-backed. They operate on the parsed workbook dict directly.

4. **No FODS-to-ODS conversion** — Family-format conversion (FODS ↔ ODS) is not yet implemented.

5. **Formula evaluation not supported** — Formula cells are read as stored strings only.
   No formula evaluation engine is included.

---

## Breaking Changes

None (first release).

---

## Installation

```bash
pip install aspose-format-factory-fods
```

Or from source:

```bash
cd src/python/fods
python -m build --wheel
pip install dist/aspose_format_factory_fods-0.1.0-py3-none-any.whl
```

---

## License

Apache-2.0
