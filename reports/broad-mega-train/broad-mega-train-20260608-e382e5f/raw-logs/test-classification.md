# Test Suite Classification
Sprint: FORMAT-FACTORY-BROAD-AUTHORITY-PRODUCT-AUTONOMY-AND-HEALING-MEGA-TRAIN-001
Run ID: broad-mega-train-20260608-e382e5f
Generated: 2026-06-08T17:10:00Z

## Key Test Runs

### Authority + ZST + FODS suites
Command: `.local/venv/Scripts/python -m pytest tests/python/zst/ tests/python/fods/ tests/supervisor/test_authority_gate_validation.py tests/supervisor/test_authority_conveyor.py tests/supervisor/test_fast_format_authority_r126.py -q`
Result: **830 passed, 8 skipped**
New tests included:
- tests/python/zst/test_r127_zst_fact_traceability.py (11 tests — FACT-ZST-001/002)
- tests/supervisor/test_authority_gate_validation.py (22 tests)
- tests/supervisor/test_authority_conveyor.py (21 tests)
- tests/supervisor/test_fast_format_authority_r126.py (21 tests)

### Full supervisor suite
Command: `.local/venv/Scripts/python -m pytest tests/supervisor/ -q`
Result: **2899 passed, 4 failed, 4 skipped**

## Pre-existing Failures (not introduced this sprint)
| Test | Failure Reason | Pre-existing |
|------|---------------|-------------|
| test_product_ledger_to_proof_graph_projection::test_real_ledger_projects_successfully | Ledger entries missing fields | YES |
| test_r90_product_acceleration::test_repo_ledger_backfills_r89_apis_and_validates | Same ledger debt | YES |
| test_validate_product_code_ledger::test_real_ledger_passes | NDJSON/TSV entries missing capability_refs/api_symbols | YES |
| test_validate_skill_registry::test_real_registry_passes | Skill registry gap | YES |

## New Tests Created This Sprint (Sprint 3+4 combined)
- tests/supervisor/test_authority_gate_validation.py — 22 tests
- tests/supervisor/test_authority_conveyor.py — 21 tests
- tests/supervisor/test_fast_format_authority_r126.py — 21 tests
- tests/python/zst/test_r127_zst_fact_traceability.py — 11 tests
Total new: **75 tests**

## ZST P6 Verification
ZST authority_level = P6 ✓ (proof graph detected by _check_proof_graph())
FODS authority_level = P6 ✓ (maintained)
Both formats: readiness_allowed=True, product_expansion_allowed=True
