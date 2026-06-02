---
sprint: R91
generated_by: r91-worker
---

# FOSS Dogfood Export

## Summary

Python Netpbm PPM→PGM installed workflow proven. R91 adds a test proving the installed package path is used. SYLK→CSV dogfood is classified as `GAP_DOGFOOD_EXTERNAL` (does not use the FF CSV library path). Dogfood strategy updated.

## Python Netpbm: PPM→PGM Dogfood

Status: IMPLEMENTED (from R90)

R91 addition: `tests/python/ppm/test_r91_ppm_to_pgm_installed.py`

### 2 New Tests

1. `test_ppm_to_pgm_uses_installed_package_path`
   - Verifies that `ppm_to_pgm` is importable from the installed ppm package (not from PYTHONPATH/src/)
   - Runs: `python -c "from ppm import ppm_to_pgm; print('ok')"` from a clean environment
   - Asserts: exit code 0

2. `test_ppm_to_pgm_installed_conversion_produces_valid_pgm`
   - Constructs a minimal PPM bytes object
   - Converts to PGM using installed package path
   - Asserts output is valid PGM (starts with `P5` or `P2` magic bytes)

Both tests pass.

## SYLK→CSV Dogfood Classification

`sylk_to_csv` uses Python's `stdlib csv` writer — it does not use the Format Factory CSV library path (`src/python/csv/`).

Classification: `GAP_DOGFOOD_EXTERNAL`

Meaning: The export works correctly and is tested, but it does not exercise the FF CSV product library. A true dogfood bridge would call `ff_csv.write_row()` or equivalent FF CSV library function.

This is documented in the dogfood strategy as a known gap. It does not block Gate 10 for SYLK. A future sprint may add a SYLK→CSV-via-FF-library bridge if the FF CSV library develops a public write API.

## Dogfood Strategy Update

`docs/automation/dogfood-strategy.md` updated:

```yaml
ppm_to_pgm_python:
  dogfood_status: IMPLEMENTED
  installed_path_verified: true
  r91_addition: installed_path_tests

sylk_to_csv:
  dogfood_status: GAP_DOGFOOD_EXTERNAL
  classification_reason: uses_stdlib_csv_not_ff_csv_library
  repair_path: add_ff_csv_write_api_and_wire_sylk_to_it
  repair_priority: low
```

## Evidence Artifacts

- `tests/python/ppm/test_r91_ppm_to_pgm_installed.py` — 2 passing tests
- `docs/automation/dogfood-strategy.md` — updated classification for sylk_to_csv
