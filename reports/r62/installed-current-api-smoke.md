# R62 Train E: Installed-Wheel API Smoke Test

**Sprint:** FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** PASS

---

## Test Environment

- Venv: `.local/r62-smoke-venv` (clean, isolated from repo)
- Installed wheels: From `.local/r62-metadata/package-artifacts/`
  - `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl`
  - `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl`
- Python: 3.13.2 (`.local/r62-smoke-venv/Scripts/python`)

---

## FODS API Smoke Results (7 APIs)

| API | Result | Notes |
|---|---|---|
| `workbook_stats(wb)` | PASS | Returns dict with sheet_count |
| `workbook_cell_range(wb)` | PASS | Returns list |
| `workbook_merged_cell_summary(wb)` | PASS | **R62 new capability** |
| `workbook_sheet_order(wb)` | PASS | **R62 new capability** |
| `make_warning(code, msg)` | PASS | Returns dict with 'code' key |
| `fods.__version__` | PASS | = 0.1.0 |
| `fods.__track__` | PASS | = python-foss |

---

## FODT API Smoke Results (7 APIs)

| API | Result | Notes |
|---|---|---|
| `document_stats(doc)` | PASS | Returns dict with block_count |
| `document_reading_level(doc)` | PASS | Returns dict |
| `document_hyperlink_count(doc)` | PASS | **R62 new capability** |
| `document_footnote_count(doc)` | PASS | **R62 new capability** |
| `make_warning(code, msg)` | PASS | Returns dict with 'code' key |
| `fodt.__version__` | PASS | = 0.1.0 |
| `fodt.__track__` | PASS | = python-foss |

---

## R62 New Capabilities Confirmed in Installed Wheel

Both new FODS capabilities (`workbook_merged_cell_summary`, `workbook_sheet_order`) and both
new FODT capabilities (`document_hyperlink_count`, `document_footnote_count`) are present and
functional in the installed wheel from `.local/r62-metadata/package-artifacts/`.

This closes IV-R61-003: Installed-wheel API proof now present in R62.

---

## Summary

**INSTALLED_WHEEL_SMOKE_R62: PASS (14/14 APIs)**
**NEW_R62_CAPABILITIES_IN_WHEEL: CONFIRMED**

Closes IV-R61-003.
