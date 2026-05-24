# R58 Evidence Bundle Validator Hardening

**Sprint:** FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
**Train:** C
**Date:** 2026-05-24

---

## Problem

R57 validator passed despite 11 structural defects. Key gaps:
- No check for `__pycache__` / `.pyc` files in bundle
- No check for state showing `Latest sprint: RXX - PENDING`
- No check for `IN_PROGRESS` lanes in scoreboard / final-verdict
- No check for sidecar committed to repo and embedded inside ZIP
- Four previously written check functions never wired into validate_bundle()

---

## New Check Functions Added

### check_pycache_in_bundle(zf)
Detects `__pycache__/` directories or `.pyc` files in the `repo/` portion of the bundle.
Error token: `BUNDLE_PYCACHE_PRESENT`

### check_state_sprint_pending(zf)
Reads `repo/state/current-state.md` and `repo/state/current-state.json` from the bundle.
Detects `Latest sprint: RXX - PENDING` or `"verdict": "PENDING"`.
Error token: `STATE_SPRINT_PENDING`

### check_repo_sidecar_not_inside_zip(zf, bundle_path)
Detects if a `.sha256-proof.json` for the current bundle is committed to the repo
(and thus embedded inside the ZIP under `repo/` path).
Error token: `SIDECAR_INSIDE_ZIP`

### check_scoreboard_lanes_in_progress(zf)
Detects `IN_PROGRESS` in `multi-mega-train-scoreboard.md` or `final-verdict.md`.
Error tokens: `SCOREBOARD_LANE_IN_PROGRESS`, `SCOREBOARD_STATUS_IN_PROGRESS`, `VERDICT_TRAIN_IN_PROGRESS`

---

## Previously Unwired Checks Now Wired

All four R56 check functions now called in validate_bundle() under --check-no-pending:
- `check_scoreboard_finality` (R56 IV-R55-004)
- `check_embedded_sidecar_bundle_match` (R56 IV-R55-003)
- `check_nested_zips_allowed` (R56 IV-R55-009)
- `check_package_claim_policy_consistency` (R56 IV-R55-002)

---

## Backward Compatibility

- `check_sidecar_proof` now accepts `bundle_sha256` as fallback for legacy R57 sidecars
- All existing R56/R57 contracts and tests continue to pass

---

## Tests Added

- tests/evidence/test_r58_bundle_hygiene_no_pyc.py (7 tests)
- tests/evidence/test_r58_state_finality_strictness.py (4 tests)
- tests/evidence/test_r58_scoreboard_finality_strictness.py (4 tests)

**All 15 new Train C tests: PASS**
**Total Train B+C: 43 tests PASS**
