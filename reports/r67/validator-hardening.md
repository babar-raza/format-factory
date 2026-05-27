# R67 Train D — Validator Hardening

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## New Validator Checks (test-level)

The following checks are implemented in R67 test files and will feed into
the formal validator in R68:

1. **PENDING_FINAL_COMMIT in any metadata file** — FAIL
   - Covers: package-artifact-manifest.yaml, dotnet-nupkg-manifest.yaml
   - Test: test_r67_no_pending_final_commit_in_metadata.py

2. **PENDING/placeholder tokens in proof files** — FAIL
   - Tokens: PENDING_FINAL_COMMIT, to be completed, to be generated, to be confirmed
   - Test: test_r67_no_placeholder_or_in_progress_metadata.py

3. **Package replay summary required** — FAIL if missing
   - extracted-package-replay-summary.txt must exist and say PASS
   - Test: test_r67_package_replay_summary_required.py

4. **Manifest hash strictness** — FAIL
   - All sha256 fields must be 64-char hex, no ellipsis truncation
   - Test: test_r67_manifest_hash_strictness.py

5. **final_git_head must be 40-char SHA** — FAIL
   - Test: test_r67_manifest_full_hashes_and_final_head.py

6. **Dotnet manifest must have filename/size/sha256** — FAIL if missing
   - Test: test_r67_manifest_hash_strictness.py

7. **Artifact source commit must be 40-char SHA** — FAIL
   - Test: test_r67_artifact_source_commit_policy.py

## Tests

- test_r67_no_pending_final_commit_in_metadata.py: 4 local + 2 bundled = 6 tests
- test_r67_package_replay_summary_required.py: 4 tests
- test_r67_no_placeholder_or_in_progress_metadata.py: 8 parametrized tests
- test_r67_manifest_hash_strictness.py: 5 local + 2 bundled = 7 tests

Total: 25 new validator hardening tests

VALIDATOR_HARDENING: COMPLETE
