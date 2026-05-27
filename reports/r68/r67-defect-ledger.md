# R68 Train A — R67 Defect Ledger

Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
Date: 2026-05-27

## Summary

Total defects: 6 (4 RC-blocking closeout-hygiene, 1 RC-blocking test-reliability, 1 informational)

| ID | Severity | Description | Train |
|---|---|---|---|
| IV-R68-001 | RC-BLOCKING | AUTHORITATIVE_TEST_RESULT stale in final-verdict.md (pre-bundle snapshot) | B + C |
| IV-R68-002 | RC-BLOCKING | python-tests-summary.txt has TBD and UNKNOWN tokens | B |
| IV-R68-003 | RC-BLOCKING | final-independent-verification.md has [to be filled] throughout | C |
| IV-R68-004 | RC-BLOCKING | lane-ownership.md has PENDING for completed trains | C |
| IV-R68-005 | RC-BLOCKING | ENV-var isolation defect in synthetic bundle discovery tests | D |
| IV-R68-006 | Informational | Validator does not check for closeout-hygiene tokens | E |

## Defect Details

### IV-R68-001

- **File:** reports/r67/final-verdict.md
- **Line:** 42 — AUTHORITATIVE_TEST_RESULT
- **Pre-bundle text:** `5118 passed, 12 failed (3 pre-existing + 6 pending bundle + 3 unknown), 27 skipped`
- **Expected post-bundle:** 6 "pending bundle" tests resolve to PASS; 3 "unknown" resolved
- **Repair:** Run post-bundle suite, update final-verdict.md + python-tests-summary.txt with authoritative count

### IV-R68-002

- **File:** .local/r67-metadata/python-tests-summary.txt
- **Tokens:** "Post-bundle authoritative count: TBD", "UNKNOWN (3 — output truncation...)"
- **Repair:** Replace TBD with actual post-bundle count; resolve or classify the 3 unknown failures

### IV-R68-003

- **File:** reports/r67/final-independent-verification.md
- **Tokens:** `[to be filled]` in every checklist row + `[to be filled at closeout]` for FINAL_IV
- **Repair:** Fill all checklist items with actual results from R67 evidence; set FINAL_IV

### IV-R68-004

- **File:** reports/r67/lane-ownership.md
- **Tokens:** PENDING for E, F, J, K, L, W1–W5
- **Evidence:** final-verdict.md shows all trains COMPLETE (or PARTIAL_DOCUMENTED for W4)
- **Repair:** Update lane status to match final-verdict.md

### IV-R68-005

- **File:** tests/packaging/test_r67_extracted_current_bundle_discovery.py
- **Root cause:** Tests do not clear FORMAT_FACTORY_BUNDLE_METADATA_DIR before running synthetic bundle assertions
- **Symptom:** When env var points to real r67-metadata (which has matching sprint-id.txt), find_artifact_dir("r67", temp_repo) returns .local/r67-metadata/package-artifacts instead of temp synthetic artifacts
- **Repair:**
  1. Add `monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)` to synthetic bundle tests
  2. Create tests/packaging/test_r68_artifact_discovery_env_isolation.py with explicit isolation proofs

### IV-R68-006

- **File:** tools/evidence/validate_evidence_bundle.py
- **Gap:** No scan for `[to be filled]`, `TBD`, `UNKNOWN (3 —`, or similar closeout-hygiene tokens in bundled final reports
- **Repair:** Add closeout-hygiene token scan in validator; create test_r68_closeout_hygiene.py
