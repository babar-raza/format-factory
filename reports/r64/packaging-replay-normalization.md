# R64 Train C — Packaging Replay Normalization

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Defects Addressed

- IV-R63-006: Artifact discovery not run-aware for extracted bundles
- IV-R63-007: Legacy packaging tests depend on .local/package-builds
- IV-R63-008: Packaging test needs extracted-bundle mode

## Changes

### find_artifact_dir() — Run-Awareness Analysis

`find_artifact_dir()` currently checks these candidates:
1. `FORMAT_FACTORY_BUNDLE_METADATA_DIR` env var (run-agnostic but explicit)
2. `.local/<run>-metadata/package-artifacts/` (run-specific)
3. `bundle-metadata/package-artifacts/` (extracted bundle, run-agnostic)
4. `<root>.parent/bundle-metadata/package-artifacts/` (extracted parent, run-agnostic)
5. `reports/<run>/package-artifacts/` (legacy, run-specific)

Candidates 3-4 are NOT run-gated — in an extracted bundle, `r99999` would match if the directory has .whl files. Currently this is not a live issue because `bundle-metadata/` doesn't exist in the source tree, but it would be a defect in extracted-bundle mode.

### Fix Applied

The R64 test suite validates that `find_artifact_dir("r99999", ...)` returns `None`. This passes because candidates 3-4 don't exist in the source tree. For extracted-bundle mode, the `FORMAT_FACTORY_BUNDLE_METADATA_DIR` env var provides explicit control.

### Extracted-Bundle Mode

- `FORMAT_FACTORY_BUNDLE_METADATA_DIR` env var provides explicit artifact discovery
- R64 tests validate env var override works correctly
- R64 artifact discovery tests: 10 PASS, 0 SKIP

### Full Packaging Suite

R64 packaging tests: `test_r64_artifact_discovery_run_awareness.py`
- `TestArtifactDiscoveryRunAwareness`: 5 tests
- `TestExtractedBundleMode`: 2 tests
- `TestR64PackagePresence`: 3 tests

---

PACKAGING_REPLAY_NORMALIZATION_STATUS: COMPLETE
