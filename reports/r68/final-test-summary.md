# R68 Train B — Final Test Summary

Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
Date: 2026-05-27

## Post-Bundle R67 Results (confirmed post-bundle)

| Category | Count |
|---|---|
| Passed | 5124 |
| Failed (pre-existing only) | 3 |
| Skipped | 27 |

## 6 Previously-Pending Bundle Tests (all now PASS)

| Test | Pre-bundle | Post-bundle |
|---|---|---|
| test_auto_proof_bundle::test_auto_proof_final_no_pending | FAIL | PASS |
| test_auto_proof_bundle::test_auto_proof_includes_final_bundle_metrics | FAIL | PASS |
| test_auto_proof_bundle::test_proof_inside_zip_is_not_candidate_only | FAIL | PASS |
| test_auto_proof_bundle::test_proof_inside_zip_has_required_fields | FAIL | PASS |
| test_r67_no_pending_final_commit_in_metadata::test_bundled_package_artifact_manifest_clean | FAIL | PASS |
| test_r67_no_pending_final_commit_in_metadata::test_bundled_dotnet_manifest_clean | FAIL | PASS |

## 3 Pre-Existing Failures (expected, pre-existing)

| Test | Reason |
|---|---|
| test_r35::test_all_contracts_have_sprint_id | R64 contract uses sprint_name (R64 reclassified) |
| test_r64::test_verdict_sidecar_sha_matches | R64 RC_REJECTED, sidecar mismatch is expected |
| test_r66_no_placeholder_metadata_proofs[validation-command-log.txt] | --check-no-pending text triggers false positive |

## 3 Collection Errors (reclassified from "unknown")

| Error | Classification |
|---|---|
| tests/ai/test_model_discovery.py | ModuleNotFoundError: httpx not in .local/venv |
| tests/ai/test_phase2_model_registry.py | ModuleNotFoundError: httpx not in .local/venv |
| (third was duplicate output truncation count) | N/A — not a real distinct failure |

Classification: Pre-existing environment gap. Not R67 defects. Not R68 scope.

## R68 New Tests (from Trains D + E)

| File | Count |
|---|---|
| tests/packaging/test_r68_artifact_discovery_env_isolation.py | 9 |
| tests/evidence/test_r68_closeout_hygiene.py | 11 |
| tests/evidence/test_r68_final_report_no_placeholders.py | 7 |
| Total new | 27 |

All 27 new R68 tests: PASS

POST_BUNDLE_PYTHON_TESTS: 5124 passed, 3 failed (pre-existing), 27 skipped
R68_NEW_TESTS: 27 added, 27 passed
