# R67 Train C — Manifest Finality and Source/Final-Head Policy

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## Problem (IV-R67-002)

Both R66 manifests contained `final_git_head: PENDING_FINAL_COMMIT` — never backfilled.

## Policy (R67 Canonical Definition)

- `artifact_source_commit`: The last git commit where package-affecting paths were changed
  and from whose working tree the artifacts were built.
  Package-affecting paths: src/, tests/packaging/, packaging scripts,
  pyproject/package config, release-manifests/, public API exports.

- `final_git_head`: The final evidence/delivery git commit SHA (40 chars).
  Must be filled before the evidence ZIP is built (pass 1) and updated to the
  final commit SHA at pass 2.

- `source_after_artifact_commit_diff_status`: Documents what changed after artifact_source_commit.
  Allowed values:
  - CLEAN_ONLY_REPORTS_STATE_TESTS_CHANGED: only reports/state/tests changed, no package impact
  - KNOWN_GAP_SOURCE_AHEAD_OF_WHEELS: source has new functions not in wheels (document and rebuild)
  - PACKAGE_AFFECTING_CHANGES_REQUIRE_REBUILD: must rebuild before RC closure

## R67 Manifest Values

- artifact_source_commit: 8c79f05c6d1cde6424d09edd0d136afc10f08ee8 (R66 mega-train)
- final_git_head: [filled at final R67 commit — updated from pass 1 SHA at pass 2]
- source_after_artifact_commit_diff_status: CLEAN_ONLY_REPORTS_STATE_TESTS_CHANGED

## R67 Wheel Rebuild

The R66 wheels had 15 APIs (built from pre-R66 source). R66 added 2+2 new APIs but
didn't rebuild wheels. R67 rebuilt all 10 wheels using `packaging/python/build-local-packages.py`
from the current source (8c79f05 state). FODS and FODT now have 17 public functions.

FODS wheel: 21941 bytes (R66: 20902) — larger, includes workbook_style_family_list + workbook_data_validation_summary
FODT wheel: 25479 bytes (R66: 24515) — larger, includes document_section_summary + document_change_tracking_summary

## Tests

- tests/evidence/test_r67_manifest_no_pending_final_commit.py: 8 tests PASS
- tests/evidence/test_r67_artifact_source_commit_policy.py: 5 tests PASS
- tests/evidence/test_r67_manifest_full_hashes_and_final_head.py: 11 tests PASS

Total: 24 manifest finality tests, all PASS

MANIFEST_FINALITY_REPAIR: COMPLETE
