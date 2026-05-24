# R61 Train I: Phase Audit 12 — RC Reproducibility

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Phase Audit 12 Scope

Phase Audit 12 focuses on RC reproducibility in the context of R61's core theme:
extracted-bundle replay and self-contained delivery.

## Audit Results

| Check | Status | Evidence |
|-------|--------|---------|
| Extracted R60 bundle: wheels discoverable without .local/ | PASS | test_r61_extracted_bundle_package_replay.py 11 tests |
| Extracted bundle: find_artifact_dir works via env-var override | PASS | 3/3 env-var tests PASS |
| R60 bundle: 10 wheels + 10 sdists present | PASS | test_r61_wheel_sdist_replay.py 10 tests |
| Wheel content: FODS/FODT APIs verifiable from bundle | PASS | test_r61_wheel_sdist_replay.py |
| SHA-256 matches between manifest and wheel on disk | PASS | test_r61_wheel_sdist_replay.py |
| .nupkg files self-contained in R61 metadata | PASS | test_r61_nupkg_self_contained.py 15 tests |
| NuGet manifest: full SHA-256 (not prefix) | PASS | test_r61_nupkg_self_contained.py |
| Bundle delivery policy: self_contained | PASS | dotnet-nupkg-manifest.yaml |
| artifact_source_commit distinct from final_git_head | PASS | test_r61_artifact_source_commit_policy.py |
| No source changes between artifact commit and final HEAD | PASS | 3 chore-only commits confirmed |
| Proof file not placeholder in final bundle | VERIFY IN M | test_r61_proof_file_not_placeholder.py |
| SHA in final-verdict matches sidecar (not interim) | VERIFY IN M | test_r61_sha_consistency_in_verdicts.py |

## Phase Audit 11 Status (from R60)

Phase Audit 11 (RC Reproducibility) was completed in R60 and marked PASS.
R61 Phase Audit 12 extends this to cover extracted-bundle replay specifically.

## Phase Audit 12 Verdict

CONDITIONAL_PASS — All extractable-bundle proof checks pass.
Placeholder proof and final SHA verification deferred to Train M (bundle build).

## New Tests Contributing to Phase Audit 12

- tests/packaging/test_r61_extracted_bundle_package_replay.py (11 tests)
- tests/packaging/test_r61_wheel_sdist_replay.py (10 tests)
- tests/dotnet/test_r61_nupkg_self_contained.py (15 tests)
- tests/packaging/test_r61_artifact_source_commit_policy.py (8 tests)

Total contributing: 44 tests, all PASS
