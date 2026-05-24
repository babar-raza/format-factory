# R60 Train D — Installed Smoke Proof

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Defects Repaired

- IV-R59-007: R59 APIs not proven from installed wheel — REPAIRED
- IV-R59-008: Installed smoke only proved R57 APIs — REPAIRED

## Environment

- Python: 3.13.2
- Install method: `pip install --force-reinstall <wheel>` into clean venv
- Venv: `.local/r60-smoke-venv/`
- Wheels tested: R60 rebuilt wheels from `.local/package-builds/python-foss/`

## FODS Installed API Smoke

```
FODS version: 0.1.0, track=python-foss

PASS workbook_type_distribution: total_cells=4, types=['string', 'float', 'empty']
PASS find_sheet_by_name: found Sales, None for X
PASS workbook_sheet_summary: 2 sheets, Sales cell_count=3
PASS workbook_empty_rows: total_empty_rows=1
```

## FODT Installed API Smoke

```
FODT version: 0.1.0, track=python-foss

PASS document_heading_outline: ['Introduction', 'Methods']
PASS document_text_content: length=73
PASS document_word_count: total=15 (blocks=6, lists=5, tables=4)
PASS document_table_summary: 1 table, rows=2, cols=2, cells=4
```

## APIs Proven (all 8 R59/R60 APIs from installed wheel)

| API | Sprint | Status |
|-----|--------|--------|
| `workbook_type_distribution` | R59 | PASS |
| `find_sheet_by_name` | R59 | PASS |
| `workbook_sheet_summary` | R60 | PASS |
| `workbook_empty_rows` | R60 | PASS |
| `document_heading_outline` | R59 | PASS |
| `document_text_content` | R59 | PASS |
| `document_word_count` | R60 | PASS |
| `document_table_summary` | R60 | PASS |

**INSTALLED_SMOKE_R60: PASS**

**TRAIN_D_COMPLETE — All R59/R60 FODS/FODT APIs proven from installed wheel**
