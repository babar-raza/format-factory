# Full Suite Failure Classification
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001
Run ID: spec-authority-full-hardening-backfill-20260608-e382e5f
Generated: 2026-06-08T18:10:00Z

## Targeted Suite (sprint-scope)
Tests run: 171
Passed: 171
Failed: 0
**Result: ALL PASS**

## Full Supervisor Suite
Tests run: 3062
Passed: 3061
Failed: 1
Skipped: 4

## Failure Classification

| Test | Root Cause | Classification | Sprint-Caused |
|------|-----------|----------------|---------------|
| test_manifest_consistency::test_evidence_artifacts_count_is_17 | Hardcoded count=17 for governance-repeatability-contracts-001 declaration which has 16 artifacts | PRE-EXISTING (verified: fails on clean checkout without our changes) | NO |

## New Tests Added This Sprint
| Test File | Tests | Result |
|-----------|-------|--------|
| tests/supervisor/test_anti_skip_sample_output_regression.py | 11 | ALL PASS |
| tests/supervisor/test_proof_graph_ledger_validation.py | 14 | ALL PASS |
Total new: 25 tests

## Prior Tests Confirmed Passing
| Test File | Tests | Result |
|-----------|-------|--------|
| test_spec_fact_refs_enforcement.py | in targeted | PASS |
| test_product_task_selector_authority_gate.py | in targeted | PASS |
| test_full_pilot_verification.py | in targeted | PASS |
| test_debt_repair_r125.py | in targeted | PASS |
| test_authority_gate_validation.py | 22 | PASS |
| test_authority_conveyor.py | 21 | PASS |
| test_fast_format_authority_r126.py | 21 | PASS |
| test_r125_fact_traceability.py (fods) | 6 | PASS |
| test_r127_zst_fact_traceability.py | 11 | PASS |

## Verdict
NO_NEW_FAILURES_INTRODUCED. Pre-existing failure (hardcoded count check) is unchanged.
