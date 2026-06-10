# Test Run Report
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Lane: F — Tests and Verification
Generated: 2026-06-05

## Test Execution Summary

| Metric | Value |
|--------|-------|
| Total tests run | 163 |
| Passed | 163 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |
| Duration | 2.17s |
| Python | 3.13.2 |
| pytest | 9.0.3 |

## Test Suite Breakdown

| Test File | Tests | Passed | Notes |
|-----------|-------|--------|-------|
| test_r3c_closure.py | 83 | 83 | R3C new tests — all PASS |
| test_real_pilot_r3.py | 41 | 41 | R3 regression — all PASS |
| test_real_pilot_r2.py | 22 | 22 | R2 regression — all PASS |
| test_real_pilots.py | 17 | 17 | R1 regression — all PASS |

## R3C New Tests Coverage (83 tests)

| Category | Count | All Pass |
|----------|-------|---------|
| R3C report file existence (17 files × 2 checks) | 34 | YES |
| Contradiction register structure and classifications | 7 | YES |
| RCA packet: 5 context packs, rca_ready, no cap claims, per-format checks | 13 | YES |
| Caveat summary: DIF anti-bypass, FODS/FODT scoped, R4 items | 5 | YES |
| Closure order protocol: defect confirmation + protocol verification | 6 | YES |
| R3 pilot results: FODT context pack deterministic + verified | 4 | YES |
| RCA packet 5-format coverage (cross-sprint) | 3 | YES |
| ODF R4 taskcards: structure, IDs, FODS/FODT coverage, plan content | 9 | YES |
| Forbidden path / allowed path checks | 3 | YES |

## Command

```
.local/venv/Scripts/python -m pytest tests/spec_authority/ -v --tb=short
```

## Raw Log Locations

- Reports: `reports/spec-authority-r3-closure-repair/raw-logs/spec-authority-r3c-tests.log`
- Evidence: `.local/evidences/spec-authority-r3-closure-repair/raw-logs/spec-authority-r3c-tests.log`

## Anti-Skip Compliance

| Rule | Status |
|------|--------|
| raw_log present | COMPLIANT — spec-authority-r3c-tests.log written in both reports/ and .local/evidences/ |
| lane_ledger_present | COMPLIANT — (this sprint is governance-only; lane-ownership.md serves as ledger) |
| test_references in declaration | WILL BE SET — evidence-declaration.yaml next |

## Regression Check

| Prior sprint | Tests | Result |
|-------------|-------|--------|
| R1 (test_real_pilots.py) | 17 | ALL PASS — no regressions |
| R2 (test_real_pilot_r2.py) | 22 | ALL PASS — no regressions |
| R3 (test_real_pilot_r3.py) | 41 | ALL PASS — no regressions |

## Verdict

`TEST_RUN_COMPLETE_163_OF_163_PASSED`
