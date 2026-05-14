---
document_type: next_sprint_recommendation
sprint: CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
title: "Post-Conway Rebaseline — Next Sprint Recommendation"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Post-Conway Rebaseline — Next Sprint Recommendation

**Sprint:** CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
**Date:** 2026-05-13

---

## Candidates Evaluated

| Candidate | Value | Risk | Urgency | Verdict |
|-----------|-------|------|---------|---------|
| Stale-detection implementation | MEDIUM | LOW | MEDIUM | Runner-up |
| Requirements tooling hardening (Phase R1) | HIGH | LOW | HIGH | **RECOMMENDED** |
| Conway Phase R2 infrastructure | MEDIUM | MEDIUM | LOW | After R1 |
| FODS/FODT entity expansion (C8+) | HIGH | MEDIUM | LOW | Blocked (need prompt quality gate) |
| Generalized command system | MEDIUM | HIGH | LOW | After R4-R5 |
| Autonomous orchestration | LOW | HIGH | LOW | Not yet |
| Evidence-contract strengthening | MEDIUM | LOW | LOW | Can merge into R1 |
| Requirements schema formalization (2 schemas) | HIGH | LOW | HIGH | MERGED INTO RECOMMENDED |
| Validator hardening | HIGH | LOW | HIGH | MERGED INTO RECOMMENDED |
| AI ledger tooling | LOW | LOW | LOW | Deferred |
| pytest/jsonschema environment stabilization | HIGH | LOW | HIGH | MERGED INTO RECOMMENDED |

---

## Recommendation

**NEXT_RECOMMENDED_SPRINT: CONWAY-PHASE-R1-SCHEMA-AND-TOOLING-HARDENING-001**

This sprint completes Conway Phase R1: schema hardening, environment stabilization, and validator strengthening.

---

## Why This Sprint

### Reason 1: Schema gaps are the highest-risk blocking item

traceability-map.yaml and verifier-review.yaml are unvalidated. These files are AUTHORITATIVE (they record accepted requirements and verifier decisions). Corruption or malformation in these files would not be caught by the current validator.

Adding schemas closes the two most important authority-chain gaps before any implementation work proceeds.

### Reason 2: pytest/jsonschema are low-effort, high-value

Installing pytest and jsonschema takes minutes. The benefit is:
- Full Draft7 schema enforcement (jsonschema) replaces manual_validate fallback
- Full test suite execution (pytest) catches regressions
- 9 existing tests can verify the validator and schemas immediately
- Conway Phase R2+ development can be tested properly

Not having these installed is a technical debt that compounds with each subsequent sprint.

### Reason 3: Fixtures make the test suite production-quality

4 fixture files (valid + 3 negative cases) allow the test suite to be run against known-good and known-bad inputs. This prevents the validator from accepting malformed files due to schema drift.

### Reason 4: This sprint has no implementation risk

No commercial capabilities are added. No entity expansion. No command files. No source changes. Risk of scope drift or governance violation is minimal.

### Reason 5: Phase R1 is a blocker for all subsequent phases

Phase R2 (context resolver) requires schemas/ to be complete. Phase R3 (lane library) requires tests/skills/ environment to be healthy. Everything downstream depends on R1 being clean.

---

## Rationale Against Other Candidates

### FODS/FODT Entity Expansion

Valid and high-value work, but currently risky without a prompt quality gate (Phase R4). An ad hoc implementation sprint for entity expansion would:
- Not have quality-gate enforcement on the implementation prompt
- Not automatically reference ACCEPTED_FOR_VERTICAL_SLICE IDs (FODS-REQ-040/041 are NEEDS_REVIEW — must not be included)
- Not enforce FODT-REQ-040 iterative traversal automatically

**Decision:** Defer until Phase R4 (prompt quality gate) exists. Or proceed manually with a careful human-crafted prompt — but this is not a Conway-skill-system activity.

### Stale-Detection Implementation

Important but not blocking today. FODS/FODT requirements are stable; no source changes expected immediately. The stale-detection rule is documented. Can be merged into Phase R1 if scope allows.

### Conway Phase R2 Infrastructure

Would be the right next step AFTER R1. Cannot safely proceed before R1 closes the schema and environment gaps.

### Autonomous Orchestration / Command System

Not safe until Phases R2-R5 are complete. Building commands before the resolver, lane library, and quality gate exist creates commands with no safety infrastructure.

---

## Recommended Sprint Scope

**Sprint ID:** CONWAY-PHASE-R1-SCHEMA-AND-TOOLING-HARDENING-001

**Authorized file paths:**
```
schemas/generated-requirements/traceability-map.schema.json  (NEW)
schemas/generated-requirements/verifier-review.schema.json   (NEW)
tests/requirements/fixtures/  (NEW directory)
tests/requirements/fixtures/fods-requirements-valid.yaml     (NEW)
tests/requirements/fixtures/fods-requirements-invalid-duplicate-ids.yaml  (NEW)
tests/requirements/fixtures/fods-requirements-invalid-ai-only-accepted.yaml  (NEW)
tests/requirements/fixtures/fods-requirements-invalid-conversion-not-scoped.yaml  (NEW)
tools/requirements/validate_generated_requirements.py  (EXTEND — add traceability-map, verifier-review validation)
reports/testing/requirements-tooling-hardening-20260513.md  (NEW — sprint report)
```

**Optional (if scope allows):**
```
tools/requirements/validate_generated_requirements.py  (EXTEND — add --check-stale flag)
```

**Prohibited:**
- No changes to generated-requirements/
- No .claude/commands/ files
- No tools/skills/ files
- No templates/
- No src/net/ or src/python/ changes
- No Gate 11 approval
- No commercial readiness claim

**Validation commands:**
```
pip install pytest jsonschema
python -m pytest tests/requirements -v  → must show 9/9 PASS minimum
python tools/requirements/validate_generated_requirements.py --format fods --verbose  → PASS
python tools/requirements/validate_generated_requirements.py --format fodt --verbose  → PASS
python tools/evidence/check_current_state_consistency.py  → CURRENT_STATE_CONSISTENCY: PASS
python tools/governance/check_methodology_links.py  → METHODOLOGY_LINK_CHECK: PASS
```

**Success criteria:**
1. 6/6 schemas present in schemas/generated-requirements/
2. All 4 validator schemas actively validate their respective files
3. traceability-map.yaml and verifier-review.yaml validated by new schemas (PASS)
4. 9+ tests pass with pytest
5. fixtures/ directory contains 4 files (valid + 3 negative)
6. REQUIREMENTS_SCHEMA_VALIDATION: PASS for fods and fodt

**Evidence contract:** Inherit from base-run.yaml; min_metadata_count: 30

**Final response format:**
1. VERDICT: SCHEMA_HARDENING_PASS | FAIL | BLOCKED
2. SCHEMAS_ADDED: list (should be 2)
3. SCHEMAS_TOTAL: count (should be 6)
4. TESTS_PASS: N/N
5. FIXTURES_ADDED: count (should be 4)
6. VALIDATOR_COVERAGE: which files now covered
7. PYTEST_INSTALLED: YES | NO
8. JSONSCHEMA_INSTALLED: YES | NO
9. NO_STASH_RESET_RESTORE_CLEAN_USED: YES
10. NO_PUSH_NO_PUBLISH: YES
11. EVIDENCE_BUNDLE: <absolute windows path>

---

## After Phase R1: Sequence Preview

```
R1: Schema + tooling hardening  ← NEXT
R2: Format context resolver
R3: Lane library (highest value for safe autonomy)
R4: Prompt generator + quality gate (enables safe implementation prompts)
R5: Evidence contract template
R6: Commands (human review required)
R7: Full tests + dry-runs (human review of generated prompts)
R8: DEC-034 IV of skill system (separate session)
R9: First new format rollout
```

**NEXT_RECOMMENDED_SPRINT: CONWAY-PHASE-R1-SCHEMA-AND-TOOLING-HARDENING-001**
