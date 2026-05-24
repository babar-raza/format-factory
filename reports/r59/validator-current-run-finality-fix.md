# R59 Train B — Validator Current-Run Finality Fix

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

---

## Root Cause Confirmed

IV-R58-006: `check_scoreboard_lanes_in_progress` iterates ALL `final-verdict.md` files in
the bundle and overwrites `verdict_content` on each match. The last file alphabetically is
`repo/reports/skills-system-hardening/20260517/final-verdict.md` which has no IN_PROGRESS.
R58's own final-verdict (with `IN_PROGRESS` Train M) is silently discarded by this overwrite.

**Evidence:**
```python
last_final_verdict = [e for e in zf.namelist()
                      if e.endswith('/final-verdict.md')][-1]
# = 'repo/reports/skills-system-hardening/20260517/final-verdict.md'
# Has no IN_PROGRESS → check passes → FALSE PASS
```

---

## Fix Applied

### `tools/evidence/validate_evidence_bundle.py`

`check_scoreboard_lanes_in_progress` now accepts `run_number: str = ""`:
- When `run_number` is provided (e.g. "R59"), loads ONLY `repo/reports/r59/final-verdict.md`
- Does NOT scan arbitrary historical final-verdicts
- Falls back to legacy scan only when `run_number=""` (no regression on old contracts)

Call site now passes `contract.get("run_number", "")` to the check.

### New check tokens

In addition to `IN_PROGRESS`, the check now also detects:
- `NOT_STARTED` — train not yet begun
- `BUNDLE_VALIDATION: PENDING` — bundle validation placeholder not resolved

### New cross-check

If scoreboard has `SCOREBOARD_STATUS: ALL_COMPLETE` but current-run verdict contains
incomplete tokens → `SCOREBOARD_VERDICT_CONTRADICTION` error (covers IV-R58-004).

---

## Tests Added

- `tests/evidence/test_r59_current_run_finality.py` — 9 tests
- `tests/evidence/test_r59_scoreboard_verdict_consistency.py` — 4 tests

**All 13 tests: PASS**

Key tests:
- `test_historical_later_path_does_not_override` — reproduces IV-R58-006 exactly
- `test_r58_scenario_reproduced` — reproduces full R58 failure scenario
- `test_train_m_in_progress_fails` — negative fixture (scoreboard complete, verdict IN_PROGRESS)
- `test_all_complete_passes` — positive fixture
- `test_not_started_train_fails` — NOT_STARTED also caught
- `test_bundle_validation_pending_fails` — BUNDLE_VALIDATION: PENDING caught

---

## Verdict

**TRAIN_B_COMPLETE** — Validator now uses `run_number` to target current-run final-verdict.
R58 scenario (skills-hardening overwrite) reproduced and proven to now FAIL correctly.
13 new tests all PASS.
