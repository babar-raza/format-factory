# R74 Python Package Install Replay

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** F

---

## Summary

All 10 Python FOSS packages rebuilt from current HEAD (R74). 6 key packages installed in
clean venv (.local/r74-smoke-venv) and smoke-tested. All installed smoke tests PASS.

---

## Rebuild Trigger

PBM and PGM wheels were stale (built before R73 added `image_pixel_stats()`). All 10 packages
rebuilt via `packaging/python/build-local-packages.py` to ensure current-HEAD state.

---

## Build Results (10/10 packages built)

| Package | Wheel SHA-256 (first 32) | Status |
|---|---|---|
| aspose-format-factory-zst | 328561e74bd7f89bf7743e429065ee12... | built |
| aspose-format-factory-fodp | fdebe858a4f098a643574aa88afbd7a7... | built |
| aspose-format-factory-fodg | b3d4173a4c38161b96ab8a2145cd7c1f... | built |
| aspose-format-factory-gnumeric | ed079be8b3b61d676b80be381d9120eb... | built |
| aspose-format-factory-abw | 6cf0c5d952de8e4568b27f8fda11265d... | built |
| aspose-format-factory-fods | fb5f155b5b5524fb2981090ece918aad... | built |
| aspose-format-factory-fodt | f043a94c56dbfd924e354d6ebea8fc19... | built |
| aspose-format-factory-pgm | 24c50589b566cbe6bbe62b688e9f1f8e... | built |
| aspose-format-factory-pbm | c4eb871807d6d5c54318fd841e4c886d... | built |
| aspose-format-factory-sylk | a0492f8dc29dc2dc01d1d165036be706... | built |

Full build report: `.local/package-builds/python-foss/build-report.json`

---

## Install Smoke (6 key packages in .local/r74-smoke-venv)

Installed: fods, fodt, zst, pbm, pgm, sylk (wheels)

### FODS
- parse_fods('multi-sheet-basic.fods'): sheet_count=2, total_cells=5
- workbook_stats, workbook_merged_cell_summary, workbook_style_family_list: PASS
- workbook_formula_list, workbook_data_validation_summary: PASS
- Version: 0.1.0.dev0 | track: python-foss | commercial_ready: False

### FODT
- parse_fodt('headings-and-paragraphs.fodt'): block_count=7
- document_stats, document_change_tracking_summary, document_section_summary: PASS
- Version: 0.1.0.dev0 | track: python-foss | commercial_ready: False

### ZST
- compress_bytes / decompress_bytes round-trip: PASS
- compress ratio on repetitive data: 0.003 (correct behavior)
- Version: 0.1.0.dev0 | track: python-foss | commercial_ready: False

### PBM (R73 rebuild — image_pixel_stats confirmed present)
- probe_pbm('2x2-checker.pbm'): exists=True
- image_pixel_stats('2x2-checker.pbm'): ok=True, total_pixels=4
- Version: 0.1.0.dev0 | track: python-foss | commercial_ready: False

### PGM (R73 rebuild — image_pixel_stats confirmed present)
- probe_pgm('2x2-gradient.pgm'): exists=True
- image_pixel_stats('2x2-gradient.pgm'): ok=True, total_pixels=4
- Version: 0.1.0.dev0 | track: python-foss | commercial_ready: False

### SYLK
- probe_sylk('minimal-2x2.slk'): exists=True
- parse_sylk('numeric-row.slk'): ok=True
- Version: 0.1.0.dev0 | track: python-foss | commercial_ready: False

---

## Source Hygiene (all 6)

All packages: __track__ = 'python-foss', __commercial_ready__ = False
SOURCE_HYGIENE: PASS

---

## Publication Status

publication_authorized: false — packages are local builds only. NOT uploaded to PyPI or any registry.

PACKAGE_INSTALL_REPLAY: PASS_6_OF_6_SMOKE_TESTS
