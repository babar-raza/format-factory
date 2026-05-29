# R73 Next-Format Advancement

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** G

---

## Summary

5 format tracks advanced. 3 with source changes (PBM, PGM + new API), 5 with new test files.

---

## Format Tracks

### PBM — image_pixel_stats() API (Source + Tests)

Source: `src/python/pbm/pbm_parser.py` — new `image_pixel_stats()` function
`src/python/pbm/__init__.py` — exports `image_pixel_stats`
Tests: `tests/python/pbm/test_r73_pbm_advancement.py` — 10 new tests

API: Returns `{ok, black_count, white_count, total_pixels, black_density, width, height, magic}`
All 10 tests: PASS

### PGM — image_pixel_stats() API (Source + Tests)

Source: `src/python/pgm/pgm_parser.py` — new `image_pixel_stats()` function
`src/python/pgm/__init__.py` — exports `image_pixel_stats`
Tests: `tests/python/pgm/test_r73_pgm_advancement.py` — 10 new tests

API: Returns `{ok, min_value, max_value, mean_approx, total_pixels, maxval, width, height, magic}`
All 10 tests: PASS

### SYLK — Advancement Tests

Tests: `tests/python/sylk/test_r73_sylk_advancement.py` — 14 new tests
Coverage: probe_dif API shape, dict API field verification, cell value_type discrimination,
capabilities API, synthetic edge cases (empty file, missing ID record, minimal valid).
All 14 tests: PASS

### ZST — Advancement Tests

Tests: `tests/python/zst/test_r73_zst_advancement.py` — 12 new tests
Coverage: round-trip correctness (empty, small, 1KB, repetitive), SHA-256 preservation,
probe_frame, validate_file.
All 12 tests: PASS
Note: `zstandard` package installed in `.local/venv` for test execution.

### DIF — Advancement Tests

Tests: `tests/python/dif/test_r73_dif_advancement.py` — 10 new tests
Coverage: probe_dif API, dict API consistency vs strict API, stats API,
capabilities API.
All 10 tests: PASS

---

## Total New Tests

| Format | Source Changed | New Tests | Result |
|---|---|---|---|
| PBM | YES (image_pixel_stats) | 10 | ALL PASS |
| PGM | YES (image_pixel_stats) | 10 | ALL PASS |
| SYLK | NO | 14 | ALL PASS |
| ZST | NO | 12 | ALL PASS |
| DIF | NO | 10 | ALL PASS |
| **Total** | 2 source + 3 test-only | **56** | **56/56 PASS** |

---

## Gate Status (unchanged — no gate promotions in Train G)

- PBM: Gate 10 local_release_candidate_ready
- PGM: Gate 10 local_release_candidate_ready
- SYLK: Gate 10 local_release_candidate_ready
- ZST: Gate 10 local_release_candidate_ready
- DIF: Gate 10 local_release_candidate_ready

Gate promotions require human IV per governance policy.

---

NEXT_FORMAT_ADVANCEMENT: PASS_5_TRACKS_56_NEW_TESTS
