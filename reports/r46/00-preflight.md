# R46 Preflight

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**Date:** 2026-05-21
**Status:** COMPLETE

---

## Run Number Confirmation

- `reports/r46/` — did not exist before this sprint (confirmed)
- `tools/evidence/contracts/r46*.yaml` — none existed before this sprint (confirmed)
- **R46 is free and uncontested**

---

## Environment

| Item | Value |
|------|-------|
| Python | 3.13.2 |
| dotnet | 10.0.204 |
| pytest-timeout | installed (module loads) |
| Platform | Windows 11 Pro |
| Shell | bash (Unix syntax) |

---

## R45 Bundle Defect Confirmation

**Critical R46 blocker #5 confirmed via zipfile inspection:**

```
FOUND: BUNDLE_VALIDATION: PENDING in bundle repo/reports/r45/final-verdict.md
```

The R45 bundle (`.local/r45-bundle.zip`) was built **before** the final-verdict.md was updated from PENDING to PASS. The validator did not catch this because `check_no_pending_reports` only scans `bundle-metadata/` files; it does not scan `repo/reports/*/final-verdict.md`.

This is the root cause of R46 blocker #5.

---

## State Snapshot

```
Formats: 22
Latest sprint: R45 (R45_TWO_PRODUCT_LOCAL_RC_BASELINE_REPLAYABLE)
Production blockers: 3 (G11-G NOT_STARTED, Gate8 AWAITING_HUMAN_APPROVAL, PACKAGE_NOT_PUSHED)
STATE_SNAPSHOT: PASS
STATE_LINT: PASS (0 errors, 2 warnings, 3 info)
```

---

## Spec-Cache Status

| Format | Cached |
|--------|--------|
| fods | YES (`.local/spec-cache/fods/`) |
| fodt | NO — not found in `.local/spec-cache/` |
| zst | YES (`.local/spec-cache/zst/`) |
| abw | YES (`.local/spec-cache/abw/`) |
| gnumeric | YES (`.local/spec-cache/gnumeric/`) |

**Gap:** FODT spec not in spec-cache. Phase Audit 1 must identify FODT spec sources.

---

## Pre-Run Test Baseline (R45)

| Suite | Result |
|-------|--------|
| tests/python/fods + fodt | 280 passed, 4 skipped |
| tests/package | 19 passed |
| tests/state/ | 30 passed |
| tests/evidence/ (excl auto_proof) | 788 passed |
| AUTHORITATIVE_TEST_RESULT (R45) | 2139 passed, 2 pre-existing fail, 4 skip |

---

## R46 Blocker Analysis

| # | Blocker | Root Cause | MT |
|---|---------|------------|----|
| 1 | No .whl/.tar.gz/.nupkg in bundle | Artifacts only in .local/, not in bundle-metadata/ | MT2 |
| 2 | Consumer proof not replayable | .local/consumer-proof/ not bundled | MT3 |
| 3 | test_r45_consumer_proof.py fails in clean env | Tests rely on .local/ which is gitignored | MT3 |
| 4 | final-verdict.md contains BUNDLE_VALIDATION: PENDING in bundle | Build-before-update sequence issue | MT1 |
| 5 | Validator doesn't check repo/reports/*/final-verdict.md | CURRENT_STATE_REPO_FILES too narrow | MT1 |
| 6 | pytest.ini timeout=120 → PytestConfigWarning | pytest-timeout not always installed | MT4 |
| 7 | No phase-by-phase system audit | New recurring requirement | MT5 |
| 8 | R45 verdict overclaimed | #1-#7 unresolved | (superseded by R46) |

---

## Requirements Validation

```
REQUIREMENTS_SCHEMA_VALIDATION: PASS
Total issues: 0
```

---

## AI Checks

- Not run in preflight (no live endpoints configured)
- Non-authoritative for sprint decisions

---

## Preflight Result

**PREFLIGHT: PASS** — all blockers identified, environment confirmed, run number free.
