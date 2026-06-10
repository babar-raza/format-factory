# Pilot Format Selection
Sprint: FORMAT-FACTORY-HOST-PROOFED-AUTONOMOUS-FORMAT-PILOT-001
Date: 2026-06-05

## Selected Formats (2)

### 1. ABW — AbiWord Document (Python FOSS)

**Gap:** `write_abw()` and `create_abw()` — no roundtrip capability yet
**Existing:** `load()`, `get_section_count()`, `get_paragraph_count()`, `extract_text()` — 25 tests pass
**Taskcard:** ABW-GATE4-001 (TASK-009 in next-sprint)
**Scope:** Add `write_abw(model, dest)` and `create_abw(paragraphs)` to `src/python/abw/abw_codec.py`
**Tests:** 8 new (roundtrip proof)
**Sample output:** `examples/python/abw/create_document_example.py`

### 2. Gnumeric — Gnumeric Spreadsheet (Python FOSS)

**Gap:** `export_to_csv()` — no CSV export yet
**Existing:** `load()`, `get_sheet_count()`, `get_cell_count()`, `extract_values()`, `get_sheet_metadata()` — 23 tests pass
**Scope:** Add `export_to_csv(model, sheet_index=0)` to `src/python/gnumeric/gnumeric_codec.py`
**Tests:** 8 new (export verification)
**Sample output:** `examples/python/gnumeric/export_csv_example.py`

## Rejected Formats

- **SVG**: PROHIBITED (Netpbm replacement rule)
- **ODS**: Higher complexity (zip extraction), deferred
- **ODT**: Higher complexity, deferred
- **XCF**: Binary format, higher risk, deferred

## Gate C Status

READY — max 2 formats selected, no broad expansion, evidence-backed selection.
