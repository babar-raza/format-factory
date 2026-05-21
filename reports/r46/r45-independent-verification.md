# R45 Independent Verification

**Sprint:** FORMAT-FACTORY-R46-ARTIFACT-CONTAINED-TWO-PRODUCT-RC-001
**IV of:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001
**Date:** 2026-05-21
**Reviewer:** R46 sprint (per DEC-034: independent session)

---

## R45 Classification

**R45 Verdict (claimed):** `R45_TWO_PRODUCT_LOCAL_RC_BASELINE_REPLAYABLE`

**R46 IV Classification:** `R45_RC_PROGRESS_ACCEPTED_ARTIFACT_AND_CONSUMER_REPLAY_PARTIAL`

**Rationale:** R45 made genuine, verified progress on all 11 R44 blockers. However, the verdict
of "REPLAYABLE" is overclaimed because:
1. The bundle contains no actual `.whl`/`.nupkg` artifacts — only hashes/logs
2. Consumer proof (`dotnet restore`/`run`) depends on `.local/` which is gitignored
3. The R45 bundle itself contains `BUNDLE_VALIDATION: PENDING` in `repo/reports/r45/final-verdict.md`
4. `pytest.ini timeout=120` causes `PytestConfigWarning` in clean envs without pytest-timeout

---

## Accepted Claims (11/11 R44 blockers closed at execution level)

| Blocker | R45 Claim | IV Result |
|---------|-----------|-----------|
| #1 .NET consumer proof not completed | MT4 4A+4B: FODS + FODT consumer PASS | ACCEPTED |
| #2 No .whl/.tar.gz/.nupkg in bundle | MT3: artifact manifest added | PARTIAL — manifests only, no artifacts |
| #3 Proof is logs/hashes only | MT3 3C: validator extended | ACCEPTED — validator extended correctly |
| #4 test_r44_timeout_portability.py fails | MT2 2A: importorskip + pytest.ini | PARTIAL — warning persists in clean envs |
| #5 test_auto_proof_bundle.py times out | MT2 2B: 9/9 PASS 50.43s | ACCEPTED — bounded execution confirmed |
| #6 cp1252 byte 0x97 in state files | MT1 1B: UTF-8 fix in state_snapshot.py | ACCEPTED — fix confirmed, tests pass |
| #7 state_snapshot.py writes without UTF-8 | MT1 1B: encoding="utf-8" added | ACCEPTED — fix confirmed |
| #8 require_clean_git: false in R44 | MT1 1C: R45 uses require_clean_git: true | ACCEPTED |
| #9 Validator too weak (only POC_READY) | MT3 3C: extended for LOCAL_RC etc. | ACCEPTED — 10 tests pass |
| #10 G11-G packet too broad | MT4 4C: Tier 0 only | ACCEPTED |
| #11 R44 insufficient product materialization | MT4 4A+4B: consumer project proof | PARTIAL — not in bundle |

**Overall:** R45 execution work is ACCEPTED. Verdict overclaim identified: "REPLAYABLE" not achieved.

---

## R45 Bundle Defect (Critical)

Confirmed via zipfile inspection: `repo/reports/r45/final-verdict.md` inside `.local/r45-bundle.zip`
contains `BUNDLE_VALIDATION: PENDING`. The validator did not catch this because:
- `check_no_pending_reports()` only scans `bundle-metadata/` files
- `check_repo_current_state_pending()` only scans `CURRENT_STATE_REPO_FILES` (plans/master-plan.md, memory/09)
- `repo/reports/*/final-verdict.md` is NOT scanned

**R46 Fix Required:** Extend validator to scan `repo/reports/*/final-verdict.md` for PENDING markers.

---

## Test Counts Verified

| Suite | R45 Claimed | IV Result |
|-------|-------------|-----------|
| tests/state/ | 30 passed | ACCEPTED |
| tests/evidence/ (excl auto_proof) | 788 passed | ACCEPTED |
| tests/evidence/test_auto_proof_bundle.py | 9 passed | ACCEPTED |
| tests/python/ | 1010 passed, 2 fail, 4 skip | ACCEPTED |
| .NET FODS | 157 passed | ACCEPTED |
| .NET FODT | 145 passed | ACCEPTED |
| **AUTHORITATIVE_TEST_RESULT** | 2139 passed | ACCEPTED |

---

## Gaps Carried Forward to R46

1. **ARTIFACT_NOT_IN_BUNDLE** — `.whl`/`.nupkg` files must be in `bundle-metadata/package-artifacts/`
2. **CONSUMER_PROOF_NOT_REPLAYABLE** — consumer projects must be rebuildable from bundled artifacts
3. **BUNDLE_PENDING_MARKER** — validator must catch `repo/reports/*/final-verdict.md` PENDING
4. **TIMEOUT_WARNING** — pytest.ini `timeout=120` causes warning without pytest-timeout
5. **FODT_SPEC_NOT_CACHED** — `.local/spec-cache/` has no fodt entry

---

## R45 Supersession

R45 verdict is superseded by R46 as:
`R45_RC_PROGRESS_ACCEPTED_ARTIFACT_AND_CONSUMER_REPLAY_PARTIAL`

R45 execution work stands. No R45 artifacts are retracted.

---

## IV Result

**IV_CLASSIFICATION:** `R45_RC_PROGRESS_ACCEPTED_ARTIFACT_AND_CONSUMER_REPLAY_PARTIAL`
**IV_STATUS:** COMPLETE
