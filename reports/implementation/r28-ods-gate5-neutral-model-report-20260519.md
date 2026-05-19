# ODS Gate 5 — Neutral Model and API Hardening Report
# Sprint: FORMAT-FACTORY-R28-GATE5-GATE7-ORACLE-FUZZ-XCF-ZPAQ-G11-C9-PUBLICATION-HARDENING-001
# Date: 2026-05-19

## Gate 5 Status: PASS

## Changes

### Source: src/python/ods/ods_parser.py
- Added `UNSUPPORTED_FEATURES` frozenset (17 features): formulas, formula_evaluation, charts, pivot_tables, conditional_formatting, data_validation, macros, embedded_objects, images, named_ranges, cell_styles, merged_cells, filters, comments, protection, encryption, external_links
- Added `SUPPORTED_FEATURES` frozenset (12 features): sheet_enumeration, cell_text_extraction, cell_value_type_detection, float_value_parsing, date_value_extraction, boolean_value_extraction, row_repeat_expansion, column_repeat_expansion, container_validation, mimetype_verification, size_guard, probe_without_parse
- Added `get_capabilities()` function returning neutral model dict

### Tests: tests/python/ods/test_ods_gate5_neutral_model.py
- 17 new tests (9 capability + 8 edge-case)
- All 17 PASS

### Edge Cases Covered
- Empty spreadsheet (0 rows)
- Multiple sheets (3-sheet parse)
- Missing body element (graceful empty return)
- Wrong mimetype (raises OdsInvalidContainerError)
- Missing content.xml (raises OdsInvalidContainerError)
- Dict API error fields (error_type present)
- Probe entries list verification

## No Gate 5 Overclaim
- commercial_product_ready: false
- Gate 5 does NOT claim production readiness
- Gate 5 adds neutral model declarations only
