# R61 Train H: Format Advancement

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## CSV Gate 8: Security Adversarial Suite

- 18 new tests in `tests/python/csv/test_r61_csv_gate8_security.py`
- Test categories: formula injection (5), malformed input (6), resource bounds (4), Unicode edge cases (3)
- All 18 tests: PASS
- CSV pack.yaml updated: `gate_8.status: pass` (sprint: R61)

### Formula Injection Coverage

| Attack Vector | Test | Result |
|--------------|------|--------|
| = prefix | `=SUM(A1:A10)` | Stored as literal string |
| + prefix | `+CMD\|/C calc` | Stored as literal string |
| @ prefix | `@SUM(1+1)` | Stored as literal string |
| Quoted injection | `"=HYPERLINK(...)"` | Stored safely |
| Nested injection | `=CONCATENATE(...)` | Stored as literal |

## Format Status Summary

| Format | Gate Status | Notes |
|--------|-------------|-------|
| CSV | Gate 8 PASS (R61) | Formula injection + security adversarial |
| TSV | Gate 7 PASS (R59) | Covered by TSV Gate 8 R60 |
| PGM/PBM/SYLK | Gate 3 PASS | Smoke tests available |
| DIF/PPM | Gate 7 PASS | Pre-existing path test failures (known) |

## DIF/PPM Pre-existing Failures

The 2 pre-existing test failures (DIF/PPM `probe_nonexistent` on Windows paths)
are documented as known issues. They do not block R61 closure:
- `test_dif_probe.py::test_probe_nonexistent_path` — Windows path format issue
- `test_ppm_probe.py::test_probe_nonexistent_path` — Windows path format issue
