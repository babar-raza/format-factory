# R67 Train B — Artifact Discovery Repair

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## Problem (IV-R67-001)

In extracted-bundle mode, `find_artifact_dir("r99999", PROJECT_ROOT)` returns
`bundle-metadata/package-artifacts` instead of `None`. The R66 fix (Train D) only
addressed the env-var override, not the `bundle-metadata/` fallback candidates.

## Root Cause

`tools/packaging/find_bundle_artifacts.py` lines 71-78 had hardcoded fallback to:
- `root / "bundle-metadata" / "package-artifacts"`
- `root.parent / "bundle-metadata" / "package-artifacts"`

These paths were returned for ANY run number if the directory existed and contained .whl files.

## Fix

Extended the sprint-id.txt pattern to both bundle-metadata/ fallback paths:
- For each bundle-metadata/ candidate, check for sprint-id.txt
- If sprint-id.txt exists, only match if run_lower appears in its content
- If no sprint-id.txt, backward-compatible behavior (allow any run)

Same pattern as R66 Train D env-var fix, applied consistently to all fallback paths.

## Tests

- tests/packaging/test_r67_artifact_discovery_no_false_positive.py: 14 tests PASS
- tests/packaging/test_r67_extracted_current_bundle_discovery.py: 5 tests PASS
- tests/packaging/test_r67_artifact_discovery_modes.py: 8 tests PASS

Total: 27 new artifact discovery tests, all PASS

## Backward Compatibility

- Bundle-metadata without sprint-id.txt: unchanged behavior (returns for any run)
- Source-tree .local/<run>-metadata/: unchanged (path embeds run, naturally specific)
- ENV_VAR override: unchanged from R66 (sprint-id.txt check already present)
- Legacy reports/<run>/: unchanged (path embeds run)

ARTIFACT_DISCOVERY_REPAIR: COMPLETE
