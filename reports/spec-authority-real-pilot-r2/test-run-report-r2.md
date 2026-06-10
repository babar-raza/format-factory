# Test Run Report — R2
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001
Generated: 2026-06-05

## Summary

| Metric | Count |
|--------|-------|
| New R2 tests | 22 |
| Existing R1 tests | 17 |
| Total tests run | 39 |
| Passed | 39 |
| Failed | 0 |
| Regressions | 0 |

**39 passed in 1.71s**

## New R2 Tests (22)

| Test | Description |
|------|-------------|
| test_r2_zst_vault_sha256_matches_real_rfc | ZST SHA is from real 112KB RFC doc |
| test_r2_netpbm_three_components_have_unique_shas | PBM/PGM/PPM have distinct SHAs |
| test_r2_fods_fetch_was_real_not_fixture | FODS tagged REAL_FETCH_SCOPED |
| test_r2_dif_stays_empirical_only | DIF authority stays EMPIRICAL_ONLY |
| test_r2_zst_classified_accepted_spec | ZST is ACCEPTED_SPEC |
| test_r2_netpbm_classified_accepted_with_caveat | Netpbm is ACCEPTED_WITH_CAVEAT |
| test_r2_zst_requirements_extracted_from_real_rfc | ZST has >=10 requirements |
| test_r2_total_requirements_substantial | Total >=40 requirements |
| test_r2_dif_requirements_do_not_exceed_fixture_count | DIF 0-50 requirements |
| test_r2_all_four_context_packs_built | ZST/Netpbm/DIF/FODS packs present |
| test_r2_context_pack_manifest_sha256_non_empty | All packs have valid SHA |
| test_r2_fods_context_pack_present | FODS pack complete (deferred in R1) |
| test_r2_context_packs_deterministic_zst | ZST deterministic |
| test_r2_context_packs_deterministic_netpbm | Netpbm deterministic |
| test_r2_context_packs_deterministic_fods | FODS deterministic |
| test_r2_all_sources_fresh | All 4 sources not stale |
| test_r2_synthetic_stale_detected_all_sources | Synthetic stale detected for all 4 |
| test_r2_sample_output_file_exists | sample-outputs/ has zst sample |
| test_r2_sample_output_has_real_manifest_sha | Sample output has valid SHA |
| test_r2_registered_citation_valid | Registered citation valid |
| test_r2_unregistered_citation_rejected | Unregistered citation rejected |
| test_r2_empirical_source_stays_empirical | DIF stays EMPIRICAL_ONLY |

## Regression Check (R1 Tests)

All 17 R1 tests continue to pass. Zero regressions.

## Raw Test Log

Located at: .local/evidences/spec-authority-real-pilot-r2/raw-logs/spec-authority-tests.log
