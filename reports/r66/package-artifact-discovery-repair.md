# R66 Package Artifact Discovery Repair

## Problem (IV-R65-006)

`find_artifact_dir("r99999")` returns current bundle artifacts when `FORMAT_FACTORY_BUNDLE_METADATA_DIR` is set, because the env-var override doesn't check the run number.

## Fix

Modified `tools/packaging/find_bundle_artifacts.py`:
- Env-var override now reads `sprint-id.txt` from the metadata directory
- If sprint-id.txt exists, the override only matches when `run_lower` appears in the sprint content
- If sprint-id.txt doesn't exist, backward-compatible behavior is preserved

## Verification

```
FORMAT_FACTORY_BUNDLE_METADATA_DIR=.local/r65-metadata
find_artifact_dir("r99999") → None (FIXED)
find_artifact_dir("r65") → .local/r65-metadata/package-artifacts (CORRECT)
```

## Tests

- tests/packaging/test_r66_artifact_discovery_no_false_positive.py: 7 tests, all PASS

PACKAGE_ARTIFACT_DISCOVERY_REPAIR: COMPLETE
