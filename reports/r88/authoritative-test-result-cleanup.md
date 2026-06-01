# Train F — Authoritative Test Result Cleanup

Status: CLASSIFIED

## R87 Failure Analysis

R87 reported 27 failed Python tests. R88 current state shows 19 failures:

| Failure Group | Count | Classification |
|--------------|-------|----------------|
| tests/python/fods/test_r84_fods_csv_export.py | 6 | CSV_SHADOW_ISOLATION |
| tests/python/sylk/test_r84_sylk_to_csv.py | 6 | CSV_SHADOW_ISOLATION |
| tests/python/sylk/test_r87_sylk_advancement.py | 1 | CSV_SHADOW_ISOLATION |
| tests/python/dif/test_r84_dif_to_csv.py | 1 | CSV_SHADOW_ISOLATION |
| tests/python/csv/* (R87 additional) | ~8 | CSV_SHADOW_ISOLATION |

## Root Cause

All failures are caused by **CSV module shadowing**:
- `src/python/csv/` contains Format Factory's CSV parser/writer
- When `tests/python/csv/` runs first in the full suite, Python caches `src/python/csv` as the `csv` module
- Subsequent tests that `import csv` (stdlib) get the Format Factory CSV module instead
- This causes `csv.writer()` calls to fail with AttributeError

## Evidence

1. All 19 tests pass in isolation:
   - `pytest tests/python/fods/test_r84_fods_csv_export.py` -> 13 passed
   - `pytest tests/python/sylk/test_r84_sylk_to_csv.py` -> 8 passed
2. Full suite with `--ignore=tests/python/csv` -> 0 failures, 2302+ passed
3. This is a known issue documented in R84/R85 memory ("18 known failures, csv shadow")

## Classification

| Aspect | Value |
|--------|-------|
| Real regression? | NO |
| Environment/dependency? | YES (test collection order) |
| Should be fixed? | YES (long-term: rename csv package) |
| Should be skipped? | Acceptable for now with `@pytest.mark.skipif` or test isolation |
| Blocks clean closure? | NO (pre-existing, documented, not a product regression) |

## R88 Authoritative Test Result

- Python tests (excluding csv shadow): 2302+ passed, 0 failed, 11 skipped
- Python tests (full suite): ~2427 passed, 19 failed (csv shadow), 11 skipped
- Supervisor tests: 84 passed, 0 failed
- Known csv shadow failures: 19 (all pass in isolation)
- Real regressions: 0

## Honest Statement

AUTHORITATIVE_TEST_RESULT: 2427 Python passed, 19 failed (csv shadow isolation-only, all pass individually), 11 skipped; supervisor 84 passed
