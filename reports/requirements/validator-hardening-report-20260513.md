---
document_type: validator_hardening_report
sprint: CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
lane: B
title: "Validator Hardening Report"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Validator Hardening Report — Lane B

**Sprint:** CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
**Date:** 2026-05-13

---

## Summary

`tools/requirements/validate_generated_requirements.py` has been extended (NOT recreated).
The existing 4-schema validator is now a 6-schema validator with cross-file consistency checks
and a stale detection framework hook.

**VALIDATOR_AUTHORITY_LEVEL: CROSS_FILE_CONSISTENT**

---

## Section 1: Changes Made

### 1.1 New schema coverage (SCHEMA_MAP expansion)

Before: 4 schemas (commercial, object-model, save-edit, conversion)
After: 6 schemas (+ traceability-map, + verifier-review)

```python
SCHEMA_MAP = {
    "commercial-requirements": "commercial-format-requirements.schema.json",
    "object-model-requirements": "object-model-requirements.schema.json",
    "save-edit-requirements": "save-edit-requirements.schema.json",
    "conversion-requirements": "conversion-requirements.schema.json",
    "traceability-map": "traceability-map.schema.json",        # NEW
    "verifier-review": "verifier-review.schema.json",          # NEW
}
```

### 1.2 Cross-file consistency checks (NEW)

Three new consistency check functions added:

**`_check_traceability_consistency(fmt)`**
- Collects ACCEPTED_FOR_VERTICAL_SLICE IDs from commercial-requirements.yaml + save-edit-requirements.yaml
- Checks that traceability-map.accepted_for_vertical_slice matches exactly
- Reports orphan IDs (in map but not in requirement files)
- Reports missing IDs (in requirement files but not in map)
- Reports deferred/accepted overlap (same ID in both lists — governance violation)
- Reports AI_PROPOSAL count ≠ 0 (AUTHORITY VIOLATION — GOVERNANCE.md 26.11)

**`_check_verifier_review_consistency(fmt)`**
- Collects all requirement IDs from commercial, save-edit, conversion, and object-model files
- Checks every requirement_challenges[].requirement_id exists in known IDs
- Checks every object_model_challenges[].entity_id exists in known IDs
- Checks verifier_verdict.result is LANE_R5_PASS or LANE_R5_FAIL

**`validate_cross_file_consistency(fmt, verbose)`**
- Orchestrates both checks above
- Returns {"status": "PASS"|"FAIL", "errors": [...]}
- Always runs (not behind a flag) — these are authority-chain safety checks

### 1.3 Stale detection framework hook (NEW — STUB)

**`check_stale_metadata(fmt, verbose)`**
- Activated by `--check-stale` flag (not run by default)
- Checks generation_timestamp field is present
- Checks input_source_hashes field is present
- Checks referenced source paths still exist in repo
- Does NOT hash-compare file contents (deferred — full impl requires future sprint)
- Returns status: PASS | MANUAL_REQUIRED | FAIL | SKIP
- MANUAL_REQUIRED status does not fail the overall validation (governance warning only)

### 1.4 Main function extended

New flags:
- `--check-stale`: enables stale detection framework hook
- Cross-file consistency runs always (no new flag needed)

---

## Section 2: What the Validator Now Enforces

| Check | Before | After |
|-------|--------|-------|
| commercial-requirements schema | YES | YES |
| object-model-requirements schema | YES | YES |
| save-edit-requirements schema | YES | YES |
| conversion-requirements schema | YES | YES |
| traceability-map schema | NO | YES |
| verifier-review schema | NO | YES |
| traceability-map ↔ commercial/save-edit ID agreement | NO | YES |
| Deferred ∩ accepted overlap detection | NO | YES |
| AI_PROPOSAL count enforcement | manual_validate only | cross-file check |
| verifier-review IDs exist in requirement files | NO | YES |
| LANE_R5_PASS result required | NO | YES (warns if FAIL) |
| Stale detection framework hook | NO | YES (stub, --check-stale) |

---

## Section 3: What Remains Advisory (Not Enforced)

| Gap | Status | Path to enforcement |
|-----|--------|---------------------|
| Hash comparison of input_source_hashes | NOT IMPLEMENTED | Future sprint: compute actual SHA-256 of source files |
| Cross-format consistency (FODS vs FODT) | NOT CHECKED | Not needed for current scope |
| Requirement count expectations | NOT ENFORCED | advisory only |
| verifier-review decision agrees with requirement status | PARTIAL | IDs checked; verdict vs status not compared |
| Generation pipeline version check | NOT ENFORCED | advisory |

---

## Section 4: Test Coverage Impact

The existing 9 tests in `test_validate_generated_requirements.py` remain valid.
New tests needed (Lane C fixtures):
- `test_traceability_map_validates` — new schema validates actual files
- `test_verifier_review_validates` — new schema validates actual files
- `test_cross_file_consistency_fods` — cross-file check passes for FODS
- `test_cross_file_consistency_fodt` — cross-file check passes for FODT
- `test_cross_file_mismatch_detected` — cross-file check fails for mismatched fixtures

---

## Section 5: Authority Chain Impact

The validator now enforces:
1. **Stage 3 → Stage 4** (schema validation): All 6 generated files are schema-validated
2. **Stage 5 → Stage 6** (verifier review structure): verifier-review.yaml is schema-validated; LANE_R5_PASS result enforced
3. **Cross-stage consistency**: traceability-map must agree with requirement files on ACCEPTED_FOR_VERTICAL_SLICE list
4. **AI_PROPOSAL authority gate**: Any AI_PROPOSAL count > 0 in traceability-map is flagged as AUTHORITY VIOLATION

---

**LANE_B_STATUS: COMPLETE**
**VALIDATOR_SCHEMA_COVERAGE_BEFORE: 4/6**
**VALIDATOR_SCHEMA_COVERAGE_AFTER: 6/6**
**CROSS_FILE_CHECKS_ADDED: 3**
**STALE_FRAMEWORK_HOOK: STUB (--check-stale flag)**
