# R67 Work-Ahead W5 — Validator Negative Fixture Library

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## Negative Fixtures Implemented

| Fixture | Implementation | Test |
|---|---|---|
| Nonexistent run artifact false positive | Synthetic extracted bundle with sprint-id.txt | test_r67_artifact_discovery_no_false_positive.py |
| PENDING_FINAL_COMMIT in manifest | Tests check actual R66 metadata (has defect) | test_r67_manifest_no_pending_final_commit.py |
| State final but invariant output FAIL | INV-003 failure tested via contract missing files | check_repo_invariants.py tests |
| Truncated artifact hash (ellipsis) | Check for "..." in sha256 lines | test_r67_manifest_hash_strictness.py |
| Missing nupkg filename/hash | dotnet manifest validation tests | test_r67_manifest_hash_strictness.py |
| Delivery package manifest mismatch | Existing R65/R66 sidecar wrong-hash tests | test_r65_delivery_package.py synthetic tests |
| Current-RC replay with required skips | test_r67_package_replay_summary_required.py | checks for PASS keyword |

W5_VALIDATOR_NEGATIVE_LIBRARY: COMPLETE
