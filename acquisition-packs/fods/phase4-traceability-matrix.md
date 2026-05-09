---
artifact_id: fods-phase4-traceability-matrix
artifact_type: acquisition-pack
path: acquisition-packs/fods/phase4-traceability-matrix.md
format_id: fods
product_family: cells
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-09"
notes: "Phase 4 Python FOSS source traceability matrix. TC-0050."
---

# FODS Phase 4 Python FOSS -- Requirements Traceability Matrix

**Package:** format-factory-fods v0.1.0
**Source:** `src/python/fods/`
**Taskcard:** TC-0050
**Gate:** Post-Gate 10 (Phase 4 Python FOSS)

---

## IR-FODS Requirements -> Source Mapping

| Req ID | Description | Source File | Function / Location | Status |
|---|---|---|---|---|
| IR-FODS-001 | office:document must be root element | parser.py | _parse_streaming() root check on first start event | IMPLEMENTED |
| IR-FODS-002 | Streaming parse -- no full-DOM load | parser.py | _ET.iterparse with elem.clear() after each row/table | IMPLEMENTED |
| IR-FODS-003 | File size guard -- max 100 MB | parser.py | parse_fods_strict() stat check; constants.py MAX_FILE_BYTES | IMPLEMENTED |
| IR-FODS-004 | defusedxml XXE protection | parser.py | Module-level try/import defusedxml, fallback to stdlib ET | IMPLEMENTED |
| IR-FODS-005 | Multi-sheet support | parser.py | _parse_streaming() QN_TABLE start/end events build sheet list | IMPLEMENTED |
| IR-FODS-006 | Row extraction | parser.py | _process_row_elem() iterates child cells of QN_ROW | IMPLEMENTED |
| IR-FODS-007 | Cell value-type dispatch | parser.py | _extract_value() dispatches on ATTR_VALUE_TYPE | IMPLEMENTED |
| IR-FODS-008 | Formula capture (eval deferred to Tier 3) | parser.py | _process_row_elem() ATTR_FORMULA captured, no eval | DEFERRED (Tier 3) |
| IR-FODS-009 | Covered cell detection | parser.py | _process_row_elem() QN_COVERED tag sets is_covered: True | IMPLEMENTED |
| IR-FODS-010 | Row repeat expansion cap (128) | parser.py | _process_row_elem() ATTR_ROW_REPEAT capped by MAX_EXPAND_REPEAT | IMPLEMENTED |
| IR-FODS-011 | Column repeat expansion cap (128) | parser.py | _process_row_elem() ATTR_COL_REPEAT capped by MAX_EXPAND_REPEAT | IMPLEMENTED |
| IR-FODS-012 | office:string-value priority | parser.py | _extract_string_value() checks ATTR_STRING_VALUE first | IMPLEMENTED |
| IR-FODS-013 | Text content fallback | parser.py | _extract_text() joins text:p children | IMPLEMENTED |
| IR-FODS-014 | Boolean normalisation (true/1 -> True) | parser.py | _extract_value() boolean branch strips and lowercases | IMPLEMENTED |
| IR-FODS-015 | draw:frame unsupported detection | parser.py | _process_row_elem() QN_DRAW_FRAME adds chart to unsupported_features | IMPLEMENTED |
| IR-FODS-016 | office:scripts macro detection (no execution) | parser.py | _parse_streaming() QN_SCRIPTS start event adds macros to unsupported_features | IMPLEMENTED |
| IR-FODS-017 | Malformed XML graceful return | parser.py | parse_fods() outer try/except catches FodsParseError, returns error dict | IMPLEMENTED |
| IR-FODS-018 | Neutral model validation before return | parser.py + neutral_model.py | _parse_streaming() calls validate_workbook(), violations become warnings | IMPLEMENTED |
| IR-FODS-019 | Whitespace strip on text values | parser.py | _extract_text() .strip() applied to joined text | IMPLEMENTED |
| IR-FODS-020 | Non-file input graceful return | parser.py | parse_fods_strict() checks path.exists() and path.is_file() | IMPLEMENTED |

---

## Coverage Summary

- **Total requirements:** 20 (IR-FODS-001 through IR-FODS-020)
- **Implemented:** 19
- **Deferred (Tier 3):** 1 -- IR-FODS-008 (formula evaluation)

## Test Coverage

| Test File | Requirements Covered |
|---|---|
| tests/python/fods/test_parser_basic.py | IR-FODS-001, IR-FODS-005, IR-FODS-006, IR-FODS-007, IR-FODS-008, IR-FODS-009, IR-FODS-010, IR-FODS-014, IR-FODS-019 |
| tests/python/fods/test_parser_malformed.py | IR-FODS-017, IR-FODS-020 |
| tests/python/fods/test_parser_security.py | IR-FODS-003, IR-FODS-004, IR-FODS-015, IR-FODS-016 |
| tests/python/fods/test_neutral_model.py | IR-FODS-018 |
| tests/python/fods/test_public_api.py | IR-FODS-001 (public API contract) |
