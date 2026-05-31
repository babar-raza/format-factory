# R85 Train M — Netpbm Reduced/FOSS Product

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Scope Decision

SCOPE: PBM + PGM + PPM (all three)
- PBM and PGM have parse + write
- PPM has parse only (write is out of R85 scope)
- PBM→PGM dogfood export: IMPLEMENTED in R85

## New work in R85

| File | Action |
|------|--------|
| src/python/pbm/pbm_to_pgm.py | NEW — PBM→PGM dogfood export using FF pgm library |
| src/python/pbm/__init__.py | UPDATED — export convert_pbm_to_pgm, pbm_pixels_to_pgm_pixels |
| tests/python/netpbm/test_r85_pbm_to_pgm_dogfood.py | NEW — 17 tests, all pass |

## Capability Audit

| Format | Load | Edit | Save | Export | Dogfood |
|--------|------|------|------|--------|---------|
| PBM | PASS | PARTIAL (pixel_stats) | PASS (write_pbm) | PBM→PGM | IMPLEMENTED |
| PGM | PASS | PARTIAL (pixel_stats) | PASS (write_pgm) | — | — |
| PPM | PASS | PARTIAL (pixel_stats) | NOT_IMPLEMENTED | — | — |

## Dogfooding

dogfood_status: IMPLEMENTED
Library: format-factory-pgm write_pgm (called from pbm.pbm_to_pgm.convert_pbm_to_pgm)
Test: tests/python/netpbm/test_r85_pbm_to_pgm_dogfood.py — 17 tests PASS
No external image library used (verified by test_no_external_image_library_imported)

## Tests

17 new tests in test_r85_pbm_to_pgm_dogfood.py:
- Unit tests for pixel conversion (9 tests)
- Integration tests with real files (6 tests)
- Dogfood library usage verification (2 tests)

## Remaining gaps

- PPM writer not implemented (out of R85 scope)
- PGM→PPM dogfood not implemented (depends on PPM writer)
- PBM→PPM cross-format via Python: NOT_YET

## TRAIN_M_STATUS: COMPLETE
