# R2 Caveat Register
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001
Generated: 2026-06-05

## Source: R2 Anti-Skip Check Result

File: .local/supervisor/reviews/spec-authority-real-pilot-r2/declaration-review-package.zip
 → review/anti-skip-check-result.json

## R2 Anti-Skip Results (14 checks)

| Check | Violation | Severity | Finding |
|-------|-----------|----------|---------|
| missing_raw_logs | NO | — | Found 2 raw log files |
| path_only_acceptance | NO | — | All accepted items have test content/criteria |
| missing_evidence_manifest | NO | — | Found 2 manifests |
| missing_report_files | NO | — | All 25 declared paths exist |
| missing_lane_ledger | **YES** | medium | No lane execution ledger found |
| missing_sample_outputs | NO | — | 1 sample output found |
| dirty_git_state | NO | — | Git state classified (wording: "clean" — misleading but not wrong) |
| evidence_quality_score | NO | — | 0.22 (2/9 verified) — non-blocking |
| declaration_completeness | NO | — | All 6 required fields present |
| test_count_regression | NO | — | 39 tests (prior=0) |

## R2 Work-Item Grade Summary

| Item | Grade | Reason |
|------|-------|--------|
| TC-R2-000 | ACCEPTED_WITH_LIMITATIONS | No test_references; path-only |
| TC-R2-001 | ACCEPTED_WITH_LIMITATIONS | No test_references; path-only |
| TC-R2-002 | ACCEPTED_WITH_LIMITATIONS | No test_references; path-only |
| TC-R2-003 | ACCEPTED_WITH_LIMITATIONS | No test_references; path-only |
| TC-R2-004 | ACCEPTED_WITH_LIMITATIONS | No test_references; path-only |
| TC-R2-005 | ACCEPTED_WITH_LIMITATIONS | No test_references; path-only |
| TC-R2-006 | **ACCEPTED_VERIFIED** | test_references + test content verified |
| TC-R2-007 | ACCEPTED_WITH_LIMITATIONS | Anti-skip files found but item not test-referenced |
| TC-R2-008 | **ACCEPTED_VERIFIED** | Final IV + review package proof present |

Root cause: Items TC-R2-000 through TC-R2-007 (except TC-R2-006) had no `test_references`
in their declaration. The grader uses `tests_with_content` as the key concrete proof dimension.

## R2 Contradictions

| ID | Contradiction | Explanation |
|----|--------------|-------------|
| C-R3-001 | Anti-skip says path_only_acceptance=false, but grades say path-only for 7/9 items | Not a real contradiction — anti-skip checks ACCEPTED_VERIFIED items only; 7 items are ACCEPTED_WITH_LIMITATIONS (different bucket). No inconsistency. |
| C-R3-002 | dirty_git_state check says "Git state is clean" but git_status_final is "dirty" | Wording mismatch only. `is_dirty=false` is correct (dirty is classified, not unclassified). Recommendation text misleading but not wrong. |
| C-R3-003 | evidence_quality_score=0.22 despite 39/39 tests passing | Not a contradiction — quality score measures ACCEPTED_VERIFIED ratio, not test pass rate. Test pass rate is 100%; item verification rate is 22%. |

## R3 Fixes

1. Add test_references to ALL 8 non-pure-coordinator work items → raises ACCEPTED_VERIFIED count
2. Create lane-execution-ledger.yaml → fixes missing_lane_ledger
3. Build FODT scoped context pack → closes R2 deferred item
4. Create rca-input-snapshot → provides downstream RCA input
5. R3 review-package-proof.md: verified no placeholders
