---
document_type: schema_hardening_report
sprint: CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
lane: A
title: "Schema Hardening Report"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Schema Hardening Report — Lane A

**Sprint:** CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
**Date:** 2026-05-13

---

## Summary

Schema coverage for `generated-requirements/` is now 6/6. Two missing schemas have been created:
- `schemas/generated-requirements/traceability-map.schema.json` (NEW)
- `schemas/generated-requirements/verifier-review.schema.json` (NEW)

**SCHEMA_COVERAGE: 6/6**

---

## Section 1: Pre-existing Schemas (4/6)

| Schema | Path | Status |
|--------|------|--------|
| commercial-format-requirements.schema.json | schemas/generated-requirements/ | EXISTED |
| object-model-requirements.schema.json | schemas/generated-requirements/ | EXISTED |
| save-edit-requirements.schema.json | schemas/generated-requirements/ | EXISTED |
| conversion-requirements.schema.json | schemas/generated-requirements/ | EXISTED |

---

## Section 2: New Schemas (2/2)

### traceability-map.schema.json

**Purpose:** Validates the generated `traceability-map.yaml` file for each format. This file maps product goals to requirement IDs and tracks the source evidence distribution for the entire requirements set.

**Authority-chain semantics encoded:**
- `source_evidence_summary.AI_PROPOSAL` is type integer with minimum 0 and annotated: "MUST be 0 for AUTHORITATIVE maps"
- `accepted_for_vertical_slice` requires minItems: 1 (authoritative maps must have at least one accepted requirement)
- `product_goal_coverage` uses enum: ["COVERED", "COVERED_FOR_VERTICAL_SLICE", "FUTURE_SCOPED", "NOT_COVERED"]
- `critical_requirements` is optional — accommodates FODT-REQ-040 iterative traversal constraint without breaking FODS validation

**Key design decisions:**
- `additionalProperties: false` at top level — strict structure
- `critical_requirements` is optional (FODT has it; FODS does not)
- `spec_citations` uses additionalProperties for dynamic spec section keys
- `source_evidence_summary` uses additionalProperties: false with explicit source type keys

**Compatible with actual files:**
- fods/traceability-map.yaml: VALID (8 top-level fields, all match schema)
- fodt/traceability-map.yaml: VALID (9 top-level fields including critical_requirements)

---

### verifier-review.schema.json

**Purpose:** Validates the `verifier-review.yaml` file produced by Lane R5 independent verifier. This is the primary authority gate document — LANE_R5_PASS is required before requirements may proceed to DEC-034 IV.

**Authority-chain semantics encoded:**
- `verifier_verdict.result` enum: ["LANE_R5_PASS", "LANE_R5_FAIL"] — explicit pass/fail gate
- `verifier_verdict.implementation_authorization.status` enum: ["AUTHORIZED", "BLOCKED", "CONDITIONAL"]
- `requirement_challenges[].verdict` enum: ["VERIFIED_ACCEPTED", "VERIFIED_ACCEPTED_WITH_NOTES", "REJECTED", "DEFERRED"]
- `global_checks` entries use result enum: ["PASS", "FAIL", "WARN"]
- `verifier_verdict.implementation_authorization.critical_constraint` is optional — accommodates FODT-REQ-040 iterative list traversal constraint
- `repair_actions_required` required (must be empty array [] for clean PASS)

**Key design decisions:**
- `global_checks` uses additionalProperties — check names are format-specific (FODT has `critical_requirement_ir_fodt_003`)
- `traceability_map_challenges` uses additionalProperties — challenge entries vary by format
- `implementation_authorization.blocked_from_implementation` is optional — FODT v FODS differ
- `additionalProperties: false` at top level and in verdict structure

**Compatible with actual files:**
- fods/verifier-review.yaml: VALID (8 required top-level fields, all match schema)
- fodt/verifier-review.yaml: VALID (same structure; critical_requirement_ir_fodt_003 in global_checks is accepted via additionalProperties)

---

## Section 3: Authority-Chain Coverage

| Gap (from authority-map report) | Status after this lane |
|----------------------------------|------------------------|
| Gap 1: traceability-map unvalidated | CLOSED — schema exists |
| Gap 2: verifier-review unvalidated | CLOSED — schema exists |
| Gap 3: AI_PROPOSAL count unchecked | DOCUMENTED in schema; enforcement in validator (Lane B) |
| Gap 4: LANE_R5_PASS structure unvalidated | CLOSED — schema enforces result enum |

---

## Section 4: Schema Design Principles Applied

1. **Draft-07 consistency** — same $schema version as existing 4 schemas
2. **additionalProperties: false** — strict where structure is known; additionalProperties allowed for dynamic maps
3. **Explicit enums** — authority states (LANE_R5_PASS/FAIL, AUTHORIZED/BLOCKED, VERIFIED_ACCEPTED/REJECTED) are enum-constrained
4. **Minimum constraints** — `accepted_for_vertical_slice` requires minItems: 1; `product_goal_coverage` requires minProperties: 1
5. **Optional fields explicit** — `critical_requirements` marked optional to support both FODS and FODT without format-specific schemas
6. **Descriptive annotations** — description fields document authority semantics for future schema readers

---

## Section 5: Gaps Not Closed by Schema Alone

These require validator logic (Lane B):
1. Cross-file consistency: `traceability-map.accepted_for_vertical_slice` vs `commercial-requirements` ACCEPTED_FOR_VERTICAL_SLICE entries
2. AI_PROPOSAL enforcement: schema annotates; validator must reject maps with AI_PROPOSAL > 0 for authoritative formats
3. Verifier-review / commercial-requirements ID agreement: every requirement_challenge must reference a known requirement ID

---

**LANE_A_STATUS: COMPLETE**
**SCHEMA_COVERAGE_BEFORE: 4/6**
**SCHEMA_COVERAGE_AFTER: 6/6**
**NEW_SCHEMAS_CREATED: 2**
