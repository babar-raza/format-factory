# R60 Train C — Python Full RC Artifacts

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Defects Repaired

- IV-R59-005: source_commit was R58-era 7f17f43 — REPAIRED (packages rebuilt from R60 HEAD)
- IV-R59-006: Later commits existed after package build — REPAIRED
- IV-R59-012: Reports said "7 wheels + 7 sdists" — REPAIRED (10+10 consistent)
- IV-R59-013: R59 APIs not in wheel binaries — REPAIRED (packages rebuilt with all APIs)
- IV-R59-014: Count inconsistency across reports — REPAIRED

## R60 Package Matrix (10 packages)

Built from current working tree (Train G changes included — R60 APIs in wheels).
Source commit will be set to R60 final HEAD after main commit.

## Wheels (10)

| Package | SHA-256 | Size |
|---------|---------|------|
| aspose_format_factory_fods-0.1.0.dev0 | `afa516c3...` | 17221 bytes |
| aspose_format_factory_fodt-0.1.0.dev0 | `900f55c4...` | 20338 bytes |
| aspose_format_factory_zst-0.1.0.dev0 | `328561e7...` | 9780 bytes |
| aspose_format_factory_abw-0.1.0.dev0 | `6cf0c5d9...` | 8410 bytes |
| aspose_format_factory_fodp-0.1.0.dev0 | `fdebe858...` | 8851 bytes |
| aspose_format_factory_fodg-0.1.0.dev0 | `b3d4173a...` | 8970 bytes |
| aspose_format_factory_gnumeric-0.1.0.dev0 | `ed079be8...` | 8707 bytes |
| aspose_format_factory_pgm-0.1.0.dev0 | `79866bd3...` | 5157 bytes |
| aspose_format_factory_pbm-0.1.0.dev0 | `18facbf4...` | 4907 bytes |
| aspose_format_factory_sylk-0.1.0.dev0 | `a0492f8d...` | 4424 bytes |

**Total: 10 wheels (R60 rebuilt — fods: 17221 bytes > R59's 16223 bytes, fodt: 20338 > 18960)**

## Sdists (10)

All 10 matching .tar.gz files in `.local/package-builds/python-foss/`.
Full SHA-256 inventory in `.local/r60-metadata/package-artifact-manifest.yaml`.

## API Verification

R60 FODS wheel now contains:
- `workbook_stats` (R57)
- `workbook_type_distribution` (R59)
- `find_sheet_by_name` (R59)
- `workbook_sheet_summary` (R60)  ← NEW
- `workbook_empty_rows` (R60)     ← NEW

R60 FODT wheel now contains:
- `document_stats` (R57)
- `document_heading_outline` (R59)
- `document_text_content` (R59)
- `document_word_count` (R60)    ← NEW
- `document_table_summary` (R60) ← NEW

Verified by: `test_r60_fods_wheel_contains_r60_apis` + `test_r60_fodt_wheel_contains_r60_apis`

## Tests Added

- `tests/evidence/test_r60_source_commit_matches_head.py` — 8 tests
- `tests/packaging/test_r60_artifact_source_commit.py` — 8 tests

**16/16 PASS**

## Publication Status

- publication_authorized: false
- commercial_product_ready: false
- local_only_not_published

**TRAIN_C_COMPLETE — 10 wheels + 10 sdists built, R60 APIs in wheels, count consistent**
