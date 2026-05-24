# R60 Train E — Packaging Test Suite Normalization

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Defects Repaired

- IV-R59-009: Package tests skip current-bundle checks — REPAIRED (R59 bundle now exists)
- IV-R59-010: Full packaging suite fails from extracted bundle — REPAIRED (env-var mode works)

## Status

The R59 packaging test skip was caused by `r59-pass2-final.zip` not yet existing when tests ran in R59. Since R59 is complete and the bundle exists, all packaging tests now pass without skips.

The R59 bundle (`.local/r59-pass2-final.zip`) was built in R59 Train M and exists at the expected path.

## Test Suite Results

```
tests/packaging/test_r59_extracted_bundle_package_replay.py: 9/9 PASS
tests/packaging/test_r59_artifact_discovery_modes.py: all PASS
tests/packaging/test_r60_artifact_source_commit.py: 8/8 PASS (new R60 test)
tests/packaging/test_python_local_package_artifacts.py: PASS (>= 7 built)
tests/packaging/test_python_installed_wheels.py: PASS
tests/packaging/test_python_local_package_imports.py: PASS
tests/packaging/test_r55_package_rc.py: PASS (>= 7 assertion)
tests/packaging/test_r56_package_rc.py: PASS
tests/packaging/test_r57_package_rc.py: PASS
tests/packaging/test_r58_extracted_bundle_replay.py: PASS
```

**No skips in packaging suite.** The `test_current_bundle_has_sdists` test that was skipping in R59
(because the R59 bundle didn't exist yet) now passes because the bundle exists.

## R60 Addition

`tests/packaging/test_r60_artifact_source_commit.py` — 8 new tests verifying:
- 10 packages built successfully
- FODS/FODT wheels contain R59/R60 APIs
- source_commit does NOT reference R58-era commit 7f17f43

**TRAIN_E_COMPLETE — No skips in packaging suite**
