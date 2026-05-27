# R68 Train D — Artifact Discovery ENV-Var Isolation

Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
Date: 2026-05-27

## Defect Repaired (IV-R68-005)

**Root cause:** `tests/packaging/test_r67_extracted_current_bundle_discovery.py` created
synthetic bundle layouts in temp directories but did NOT clear
`FORMAT_FACTORY_BUNDLE_METADATA_DIR` before calling `find_artifact_dir()`. When the env
var was globally set (pointing to `.local/r67-metadata` which has matching sprint-id.txt),
`find_artifact_dir("r67", temp_repo)` returned the real r67-metadata path instead of the
synthetic temp bundle path.

## Fix Applied

**File:** `tests/packaging/test_r67_extracted_current_bundle_discovery.py`

Added `monkeypatch.delenv("FORMAT_FACTORY_BUNDLE_METADATA_DIR", raising=False)` to all
5 test methods in `TestCurrentBundleDiscovery`. This ensures that env-var state from the
process environment cannot contaminate synthetic bundle isolation tests.

## New Test File

**File:** `tests/packaging/test_r68_artifact_discovery_env_isolation.py`

9 tests across 3 classes:
- `TestEnvVarIsolation` (3): cleared env var — synthetic bundle found correctly
- `TestEnvVarMatchBehaviour` (4): env var set with matching/mismatching sprint-id.txt
- `TestEnvVarSprint67Regression` (2): R67 regression proof — clearing env after set gives correct result

## Test Results

| File | Tests | Result |
|---|---|---|
| test_r67_extracted_current_bundle_discovery.py | 5 | 5 PASS |
| test_r68_artifact_discovery_env_isolation.py | 9 | 9 PASS |
| Total | 14 | 14 PASS |

## Verification Commands

```
FORMAT_FACTORY_BUNDLE_METADATA_DIR=".local/r67-metadata" \
  .local/venv/Scripts/python -m pytest \
  tests/packaging/test_r67_extracted_current_bundle_discovery.py \
  tests/packaging/test_r68_artifact_discovery_env_isolation.py -v
```
Expected: 14 passed

TRAIN_D_CLOSEOUT: COMPLETE
