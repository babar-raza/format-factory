# R67 Train A — R66 Defect Ledger

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001
Date: 2026-05-27

## Summary

Total defects: 3 (2 RC-blocking, 1 informational)

| ID | Severity | Description | Train |
|---|---|---|---|
| IV-R67-001 | RC-BLOCKING | Artifact discovery false positive in extracted-bundle mode | B |
| IV-R67-002 | RC-BLOCKING | PENDING_FINAL_COMMIT in package manifests | C |
| IV-R67-003 | Informational | Validator does not fail on PENDING_FINAL_COMMIT | D |

## Defect Details

### IV-R67-001

- **File:** tools/packaging/find_bundle_artifacts.py
- **Lines:** 71-78 (bundle-metadata fallback candidates)
- **Expected:** find_artifact_dir("r99999") returns None in extracted-bundle mode
- **Actual:** find_artifact_dir("r99999") returns bundle-metadata/package-artifacts
- **Repair:** Add sprint-id.txt check to bundle-metadata/ fallback paths, same as env-var override

### IV-R67-002

- **Files:** .local/r66-metadata/package-artifact-manifest.yaml, dotnet-nupkg-manifest.yaml
- **Field:** final_git_head: PENDING_FINAL_COMMIT
- **Expected:** final_git_head: 1f92d31eeb449b93fdc6bf96e865d942374eb259
- **Repair:** Backfill with actual final git HEAD SHA

### IV-R67-003

- **File:** tools/evidence/validate_evidence_bundle.py
- **Gap:** No check for PENDING_FINAL_COMMIT token
- **Repair:** Add PENDING_FINAL_COMMIT to forbidden tokens list in validator
