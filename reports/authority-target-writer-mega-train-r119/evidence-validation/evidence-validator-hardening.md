# Evidence Validator Hardening
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001
Lane: G

## Scope
This sprint adds targeted tests for the known evidence detection failure modes from
bundles 98 (Spec R3C) and 99 (RCA R1). No changes are made to the anti-skip detector
itself — only tests documenting and regression-testing the known failure modes.

## Known Failure Mode 1: Post-Cycle Artifacts Flagged as Missing

### Problem
`anti_skip_checker.py` checks for `review-package-proof.md` and `final-git-status.txt`
but these artifacts cannot exist before `autonomous-cycle` runs (they reference the ZIP SHA).

### Current Behavior
- Anti-skip correctly fires on MISSING artifacts (by design)
- False-positive: fires on review-package-proof.md which is INTENTIONALLY post-cycle
- Classification: this is a LOW severity documentation issue, not a blocker

### Recommended Fix (not implemented this sprint — design only)
Add `post_cycle_artifacts` list to evidence declaration schema:
```yaml
meta:
  post_cycle_artifacts:
    - review-package-proof.md
    - final-git-status.txt
```
Anti-skip should skip these entries when checking for missing files.

### Test Added
`tests/supervisor/test_r119_evidence_detection.py::TestReviewPackageProofProtocol`

---

## Known Failure Mode 2: Raw Logs Not in Anti-Skip Path

### Problem
In RCA R1, raw logs were in `reports/requirement-capability-real-pilot-r1/raw-logs/`
but not listed as `type: raw_log` in `evidence_artifacts` in the declaration.
Anti-skip only detects raw logs via evidence_artifacts type entries.

### Resolution
R119 declaration explicitly lists all raw logs with `type: raw_log`:
- `rca-tests-r119.log`
- `csv-writer-tests.log`
- `fods-tests.log`

### Test Added
`tests/supervisor/test_r119_evidence_detection.py::TestRawLogDetection`

---

## Known Failure Mode 3: Missing Sample Outputs

### Problem
RCA R1 had no sample output files at all.
Anti-skip flags this as a violation when dogfood work is claimed.

### Resolution
R119 produces FODS → CSV sample output:
`reports/authority-target-writer-mega-train-r119/fods-csv-integration/fods-csv-output-sample/`

### Test Added
`tests/supervisor/test_r119_evidence_detection.py::TestSampleOutputDetection`

---

## Tests Added: `tests/supervisor/test_r119_evidence_detection.py`
- TestReviewPackageProofProtocol (5 tests)
- TestRawLogDetection (4 tests)
- TestSampleOutputDetection (2 tests)
- TestFinalGitStatus (1 test)
- TestKnownFailureRegression (4 tests)

## Lane G Verdict: ACCEPT_WITH_CAVEATS
Targeted tests added. Known failure modes documented. Detector itself not modified (design only).
Broader anti-skip redesign deferred to future sprint.
