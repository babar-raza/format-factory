# R60 Defect Ledger

**Sprint Being Verified:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**IV Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24

| ID | Severity | Category | Description | R61 Repair Train | Status |
|----|----------|----------|-------------|-----------------|--------|
| IV-R60-001 | critical | sidecar | Sidecar not in ZIP — local-only, cannot validate offline | Train B | OPEN |
| IV-R60-002 | critical | sha | Pass 2 SHA in final-verdict (d2ab8404) ≠ true final bundle SHA (f8b6f8ce) | Train B | OPEN |
| IV-R60-003 | high | validation | Validation fails without sidecar argument; no standalone validation | Train B | OPEN |
| IV-R60-004 | high | proof | final-bundle-validation-proof.txt is PLACEHOLDER inside bundle | Train B | OPEN |
| IV-R60-005 | high | packaging | test_r60_artifact_source_commit.py hardcodes .local/package-builds path | Train C | OPEN |
| IV-R60-006 | high | packaging | No test_r60_extracted_bundle_package_replay.py — R60 replay untested | Train C | OPEN |
| IV-R60-007 | critical | dotnet | .nupkg files not in bundle; paths are local-only | Train F | OPEN |
| IV-R60-008 | high | dotnet | dotnet-nupkg-manifest.yaml uses sha256_prefix (8 char) not full SHA-256 | Train F | OPEN |
| IV-R60-009 | high | commit | source-commit-proof.txt calls 61780e4 "FINAL HEAD"; true final is 1171b4f | Train D | OPEN |
| IV-R60-010 | medium | reports | Reports describe 61780e4 as R60 final HEAD; inaccurate | Train D | OPEN |
| IV-R60-011 | medium | policy | No artifact_source_commit / final_git_head policy or validator enforcement | Train D | OPEN |
| IV-R60-012 | medium | replay | R60 extracted-bundle replay not proven end-to-end | Train E+M | OPEN |

## Closure Criteria

Each defect must have:
1. Evidence of repair (code change, test, or proof file)
2. At least one new test confirming the repair (where applicable)
3. Status changed to CLOSED in this ledger before Train M bundle build

## Acceptance Threshold

All 3 CRITICAL defects MUST be closed before R61 claims closure.
All HIGH defects MUST be closed or have documented exception.
MEDIUM defects MUST be closed or deferred with rationale.
