# R34 Contract Schema Migration Report

**Sprint:** FORMAT-FACTORY-R34-CLEAN-CLOSURE-AUTHORITY-PIPELINE-REPAIR-SWARM-001
**Date:** 2026-05-20

## Root Cause

The evidence bundle validator (`tools/evidence/validate_evidence_bundle.py`, line 407) reads
`required_repo_files` from contracts. Six contracts used `required_artifacts` instead, causing
the validator to see zero required repo files — silently passing validation with no file checks.

## Affected Contracts

| Contract | Old Key | New Key | Commit |
|----------|---------|---------|--------|
| r31-ai-system-isolation-and-pipeline-verification.yaml | required_artifacts | required_repo_files | 8fe020c |
| r32-ai-clean-closure-status-repair-and-pipeline-deepening.yaml | required_artifacts | required_repo_files | 8fe020c |
| r32-truth-matrix-gate-quality-and-drift-recovery.yaml | required_artifacts | required_repo_files | 8fe020c |
| r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation.yaml | required_artifacts | required_repo_files | 8fe020c |
| r33-drift-recovery-overclaim-deepening.yaml | required_artifacts | required_repo_files | 8fe020c |
| r34-r33-scope-separation-repair.yaml | required_artifacts | required_repo_files | 8fe020c |

## Verification

- `grep -l "required_artifacts" tools/evidence/contracts/*.yaml` returns ZERO matches
- 239 guard tests pass (test_contract_schema_migration.py):
  - TestNoRequiredArtifactsKey: all contracts checked
  - TestRequiredRepoFilesNonEmpty: sprint contracts verified
  - TestMetadataFloorCompliance: R23+ sprint contracts >= 30
  - TestValidatorReadsCorrectKey: validator source verified

## Impact

All 6 affected contracts now have their required_repo_files validated by the bundle validator.
Future contracts using the wrong key will be caught by the guard test suite.
