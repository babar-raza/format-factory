# R89 Train E: CSV Shadow Root Fix

## Sprint
FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## Root Cause
`tests/python/csv/__init__.py` made the test directory a Python package. When pytest
(prepend importmode) added `tests/python/` to `sys.path`, `import csv` in any module
resolved to `tests/python/csv/__init__.py` instead of stdlib `csv`. This empty
`__init__.py` lacked `csv.writer`, `csv.reader`, etc., causing 19 test failures in
FODS, SYLK, and DIF CSV export tests.

Secondary factor: `src/python/csv/__init__.py` (the Format Factory CSV package) also
shadows stdlib csv when `src/python/` is on `sys.path`, but this was masked by the
test-directory shadow taking priority.

## Fix (two-layer)
1. **Removed `tests/python/csv/__init__.py`** — eliminates the test-directory shadow.
   CSV tests still work because they import via `from src.python.csv.csv_stats import ...`
   (full dotted path), not via `import csv`.

2. **Pinned stdlib csv in `tests/python/conftest.py`** — defense-in-depth. Pre-imports
   stdlib csv before `src/python/` is added to `sys.path`, then sets
   `sys.modules["csv"] = _stdlib_csv` to prevent any future override.

## Files Changed
- `tests/python/csv/__init__.py` — DELETED (root cause)
- `tests/python/conftest.py` — added stdlib csv pre-import and sys.modules pin
- `tests/python/test_r89_csv_shadow_fix.py` — NEW: 9 regression tests

## Test Results
- Before fix: 19 failures in full-suite collection (csv+fods+sylk+dif)
- After fix: 0 failures, 2446 passed, 11 skipped (full `tests/python/`)
- Regression tests: 9/9 pass
- Supervisor tests: 84/84 pass (no impact)

## Status: COMPLETE
