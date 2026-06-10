# Test Run Report
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001
Lane: G — Tests and Validation
Generated: 2026-06-05

## Test Execution Summary

| Metric | Value |
|--------|-------|
| Total tests run | 80 |
| Passed | 80 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |
| Duration | 1.80s |
| Python | 3.13.2 |
| pytest | 9.0.3 |

## Test Suite Breakdown

| Test File | Tests | Passed | Notes |
|-----------|-------|--------|-------|
| test_real_pilot_r2.py | 22 | 22 | R2 regression — all PASS |
| test_real_pilot_r3.py | 41 | 41 | R3 new tests — all PASS |
| test_real_pilots.py | 17 | 17 | R1 regression — all PASS |

## R3 New Tests Coverage

| Category | Count | All Pass |
|----------|-------|---------|
| FODT context pack (built, SHA, deterministic, verified) | 8 | YES |
| FODT sample output anti-skip | 3 | YES |
| Lane ledger anti-skip fix | 4 | YES |
| RCA input snapshot (5 sources, caveats, rca_ready) | 10 | YES |
| FODS/FODT scoped authority non-overclaim | 6 | YES |
| R3 report files existence | 6 | YES |
| R2 regression carry-over | 4 | YES |

## Command

```
.local/venv/Scripts/python -m pytest tests/spec_authority/ -v
```

## Raw Log Location

- Reports: `reports/spec-authority-real-pilot-r3/raw-logs/spec-authority-r3-tests.log`
- Evidence: `.local/evidences/spec-authority-real-pilot-r3/raw-logs/spec-authority-r3-tests.log`

## Anti-Skip Compliance

| Rule | Status |
|------|--------|
| raw_log present | COMPLIANT (spec-authority-r3-tests.log written) |
| sample_output present | COMPLIANT (fodt-context-pack-sample.json) |
| lane_ledger present | COMPLIANT (lane-execution-ledger.yaml in reports/spec-authority-real-pilot-r3/) |
| test_references in declaration | WILL BE SET (evidence declaration next) |

## Verdict

`TEST_RUN_COMPLETE_80_OF_80_PASSED`
