# R74 Product Advancement Verification

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** E

---

## Purpose

Verify that R73 product advancement changes (Trains D and G) are real, testable, and still passing
in the current HEAD. Confirm no regressions from R74 changes (ZST fix, validator hardening).

---

## R73 Product Advancement Inventory

### FODS Source Changes (R73 Train D)

| Change | File | Constants Added |
|---|---|---|
| Merged cell span preservation | src/python/fods/parser.py | ATTR_COL_SPAN, ATTR_ROW_SPAN |
| Formula cell warning code | src/python/fods/parser.py | WARN_FORMULA_CELL |

Verification: constants.py and parser.py contain these additions (committed in 5cdde46).
Test file: `tests/python/fods/test_r73_fods_merged_cell_span.py` — 8 tests.

### FODT Source Changes (R73 Train D)

| Change | File | Constants Added |
|---|---|---|
| Footnote/endnote detection warning | src/python/fodt/parser.py | QN_TEXT_NOTE, WARN_NOTE_ELEMENT |
| Table cell span preservation | src/python/fodt/parser.py | ATTR_TABLE_COL_SPAN, ATTR_TABLE_ROW_SPAN |

Verification: constants.py and parser.py contain these additions (committed in 5cdde46).
Test file: `tests/python/fodt/test_r73_fodt_note_and_cell_span.py` — 8 tests.

### PBM Source Changes (R73 Train G)

| Change | File | API Added |
|---|---|---|
| image_pixel_stats() | src/python/pbm/pbm_parser.py | Returns black_count, white_count, total_pixels, black_density |
| Export | src/python/pbm/__init__.py | image_pixel_stats in __all__ |

Test file: `tests/python/pbm/test_r73_pbm_advancement.py` — 10 tests.

### PGM Source Changes (R73 Train G)

| Change | File | API Added |
|---|---|---|
| image_pixel_stats() | src/python/pgm/pgm_parser.py | Returns min_value, max_value, mean_approx, total_pixels |
| Export | src/python/pgm/__init__.py | image_pixel_stats in __all__ |

Test file: `tests/python/pgm/test_r73_pgm_advancement.py` — 10 tests.

### Test-Only Advancement Tracks (R73 Train G)

| Format | Test File | Tests |
|---|---|---|
| SYLK | test_r73_sylk_advancement.py | 14 |
| ZST | test_r73_zst_advancement.py | 12 |
| DIF | test_r73_dif_advancement.py | 10 |

---

## R74 Verification Run

All 72 R73 product advancement tests run from `.local/venv` at R74 HEAD (after ZST Unicode fix):

```
pytest tests/python/fods/test_r73_fods_merged_cell_span.py
      tests/python/fodt/test_r73_fodt_note_and_cell_span.py
      tests/python/pbm/test_r73_pbm_advancement.py
      tests/python/pgm/test_r73_pgm_advancement.py
      tests/python/sylk/test_r73_sylk_advancement.py
      tests/python/zst/test_r73_zst_advancement.py
      tests/python/dif/test_r73_dif_advancement.py

Result: 72 passed, 0 failed in 1.45s
```

No regressions. R74 changes (ZST encoding fix, validator hardening) do not affect product tests.

---

## Current Exported API Count

| Package | Exported APIs (non-exception, non-constant) |
|---|---|
| FODS | 21 (parse_fods, parse_fods_strict, write_fods, workbook_to_xml + 17 workbook_*) |
| FODT | 21 (parse_fodt, parse_fodt_strict, write_fodt, document_to_xml + 17 document_*) |
| PBM | image_pixel_stats (added R73) |
| PGM | image_pixel_stats (added R73) |
| SYLK | probe_sylk, parse_sylk, parse_sylk_strict, sylk_capabilities |
| ZST | compress_bytes, decompress_bytes, probe_frame, validate_file |
| DIF | probe_dif, parse_dif, parse_dif_strict, dif_stats, dif_capabilities |

---

## Carry-Forward Assessment

All R73 product advancement is real and verified. No source or test changes need repair in R74.

The ZST encoding fix (Train D) is carry-forward: enables clean subprocess test execution on Windows.
No API surface change — only affects print statement encoding safety.

Gate status (unchanged from R73):
- FODS: Gate 10 local_release_candidate_ready
- FODT: Gate 10 local_release_candidate_ready
- PBM: Gate 10 local_release_candidate_ready
- PGM: Gate 10 local_release_candidate_ready
- SYLK: Gate 10 local_release_candidate_ready
- ZST: Gate 10 local_release_candidate_ready
- DIF: Gate 10 local_release_candidate_ready

Gate promotions require human IV per governance policy. None claimed here.

PRODUCT_ADVANCEMENT_VERIFICATION: PASS_72_TESTS_CONFIRMED_0_REGRESSIONS
