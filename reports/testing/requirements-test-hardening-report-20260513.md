---
document_type: test_hardening_report
sprint: CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
lane: C
title: "Requirements Test Hardening Report"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Requirements Test Hardening Report — Lane C

**Sprint:** CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
**Date:** 2026-05-13

---

## Summary

Test suite is now fully operational. pytest and jsonschema are installed.
All 32 tests PASS (9 original + 23 new tests from Lane C + cross-file + new schema tests).

**TEST_SUITE_STATUS: 32/32 PASS**

---

## Section 1: Environment

| Component | Status | Version |
|-----------|--------|---------|
| Python | INSTALLED | 3.13.2 |
| pytest | INSTALLED | 9.0.3 (user site-packages) |
| jsonschema | INSTALLED | 4.25.1 (user site-packages) |
| PyYAML | INSTALLED | pre-existing |
| PYTHONPATH note | `C:/Users/prora/AppData/Roaming/Python/Python313/site-packages` needed |

**Note:** pytest installed to user site-packages (`%APPDATA%\Python\Python313\site-packages`).
Run with: `PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages python -m pytest tests/requirements -v`

---

## Section 2: Test Fixtures Created

| Fixture | Purpose | Expected Result |
|---------|---------|-----------------|
| `valid-commercial-requirements.yaml` | Minimal valid commercial requirement | PASS |
| `invalid-duplicate-ids.yaml` | Two requirements with same ID | FAIL — Duplicate error |
| `invalid-ai-only-accepted.yaml` | AI_PROPOSAL requirement marked ACCEPTED | FAIL — AI_PROPOSAL error |
| `invalid-conversion-not-scoped.yaml` | Conversion req with sprint_scope=current | FAIL — scope error |
| `valid-traceability-map.yaml` | Minimal valid traceability map | PASS |
| `cross-file-mismatch-traceability-map.yaml` | Traceability map with nonexistent req ID | FAIL — cross-file error |
| `stale-metadata-commercial-requirements.yaml` | Stale source path reference | WARN (MANUAL_REQUIRED) |

All fixtures are deterministic (no randomized IDs, timestamps, or paths).

---

## Section 3: Test Results

```
32 passed in 1.89s

TestManualValidate (9 tests):
  [PASS] test_valid_document_passes
  [PASS] test_missing_required_top_level_field
  [PASS] test_empty_requirements_array
  [PASS] test_duplicate_requirement_ids
  [PASS] test_ai_proposal_cannot_be_accepted
  [PASS] test_accepted_for_vertical_slice_requires_tests
  [PASS] test_non_product_decision_requires_source_evidence
  [PASS] test_product_decision_does_not_require_source_evidence
  [PASS] test_conversion_requirement_future_scope

TestValidateFormatIntegration (19 tests):
  [PASS] test_fods_requirements_exist
  [PASS] test_fodt_requirements_exist
  [PASS] test_fods_commercial_requirements_file_exists
  [PASS] test_fodt_commercial_requirements_file_exists
  [PASS] test_fods_requirements_validate
  [PASS] test_fodt_requirements_validate
  [PASS] test_fods_has_accepted_for_vertical_slice
  [PASS] test_fodt_has_accepted_for_vertical_slice
  [PASS] test_conversion_requirements_are_future_scoped
  [PASS] test_fods_traceability_map_exists       [NEW]
  [PASS] test_fodt_traceability_map_exists       [NEW]
  [PASS] test_fods_verifier_review_exists        [NEW]
  [PASS] test_fodt_verifier_review_exists        [NEW]
  [PASS] test_fods_verifier_review_is_lane_r5_pass  [NEW]
  [PASS] test_fodt_verifier_review_is_lane_r5_pass  [NEW]
  [PASS] test_fods_cross_file_consistency        [NEW]
  [PASS] test_fodt_cross_file_consistency        [NEW]
  [PASS] test_fods_ai_proposal_count_is_zero     [NEW]
  [PASS] test_fodt_ai_proposal_count_is_zero     [NEW]

TestFixtures (4 tests):
  [PASS] test_valid_fixture_passes
  [PASS] test_duplicate_ids_fixture_fails
  [PASS] test_ai_only_accepted_fixture_fails
  [PASS] test_conversion_not_scoped_fixture_fails
```

---

## Section 4: Validator Direct Run Results

```
FODS: 6/6 PASS (commercial, object-model, save-edit, conversion, traceability-map, verifier-review)
      cross-file-consistency: PASS
      Total issues: 0

FODT: 6/6 PASS (all same files)
      cross-file-consistency: PASS
      Total issues: 0

REQUIREMENTS_SCHEMA_VALIDATION: PASS
```

---

## Section 5: Gaps Not Closed

| Gap | Status |
|-----|--------|
| pytest in PATH permanently | Requires PATH modification or use PYTHONPATH prefix |
| CI/CD environment setup | Not configured (future sprint) |
| Schema validation with jsonschema for traceability/verifier files | NOW WORKS (jsonschema 4.25.1 installed) |

---

**LANE_C_STATUS: COMPLETE**
**TEST_COUNT_BEFORE: 9**
**TEST_COUNT_AFTER: 32**
**ALL_PASS: YES (32/32)**
**PYTEST_INSTALLED: YES**
**JSONSCHEMA_INSTALLED: YES**
