---
document_type: authority_map
sprint: CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
title: "Generated Requirements Authority Map"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Generated Requirements Authority Map

**Sprint:** CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
**Date:** 2026-05-13

---

## Overview

This document maps the complete authority chain for the generated requirements system, from
upstream sources through to implementation authorization. Each stage changes the authority
status of the artifact.

---

## Section 1: Full Authority Chain

```
STAGE 0: Human Product Goals (AUTHORITY: HUMAN)
  ├── docs/commercial-product-capability-model.md
  ├── PG-001: Load + DOM
  ├── PG-002: Inspect + manipulate
  ├── PG-003: Edit entities
  ├── PG-004: Save + round-trip
  └── PG-005: Export/convert

STAGE 1: Upstream Sources (AUTHORITY: VARIES by source type)
  ├── LOCAL SPEC (AUTHORITY: SPEC — highest non-human)
  │   └── .local/spec-cache/{format}/ (cached, SHA-256 verified)
  ├── NORMALIZED SPEC (AUTHORITY: DERIVED FROM SPEC)
  │   └── .local/spec-cache/{format}/normalized/text.txt, pages.jsonl
  ├── ACQUISITION PACK (AUTHORITY: VERIFIED FACT)
  │   ├── acquisition-packs/{format}/verified-facts.yaml
  │   ├── acquisition-packs/{format}/implementation-requirements.yaml
  │   ├── acquisition-packs/{format}/tier-map.yaml
  │   └── acquisition-packs/{format}/security-surface.yaml
  ├── NEUTRAL MODEL (AUTHORITY: VERIFIED FACT)
  │   └── schemas/neutral-model/{format}/model.yaml
  ├── EXISTING SOURCE (AUTHORITY: EXISTING_SOURCE — high)
  │   └── src/net/{format}/ (confirmed existing)
  └── EXISTING TESTS (AUTHORITY: TEST_EVIDENCE)
      └── tests/net/{format}/ (confirmed existing)

STAGE 2: AI Retrieval and Synthesis (AUTHORITY: AI_PROPOSAL — LOW)
  ├── AI reads upstream sources
  ├── AI extracts structured requirements
  ├── All AI output tagged source_type: AI_PROPOSAL or grounded type
  └── Cannot become ACCEPTED_FOR_VERTICAL_SLICE at this stage

STAGE 3: Generated Requirements (AUTHORITY: PROPOSAL)
  ├── generated-requirements/{format}/commercial-requirements.yaml
  ├── generated-requirements/{format}/object-model-requirements.yaml
  ├── generated-requirements/{format}/save-edit-requirements.yaml
  ├── generated-requirements/{format}/conversion-requirements.yaml
  ├── generated-requirements/{format}/traceability-map.yaml
  └── Status: All start as AI_PROPOSAL — NOT yet authoritative
  └── Authority: NONE until Stage 4

STAGE 4: Schema Validation (AUTHORITY GATE — HARD BLOCKER)
  ├── tools/requirements/validate_generated_requirements.py
  ├── schemas/generated-requirements/*.schema.json (4 schemas)
  ├── PASS: Requirements may proceed to Stage 5
  └── FAIL: Requirements BLOCKED — cannot proceed

STAGE 5: Verifier Review (AUTHORITY: CONDITIONAL)
  ├── generated-requirements/{format}/verifier-review.yaml
  ├── Conducted by: separate verifier agent pass (LANE-R5)
  ├── Challenge: adversarial per-requirement challenges
  ├── Output verdicts: VERIFIED_ACCEPTED | VERIFIED_ACCEPTED_WITH_NOTES | REJECTED | DEFERRED
  ├── Result file: verifier-review.yaml (LANE_R5_PASS | LANE_R5_FAIL)
  ├── PASS: Requirements marked ACCEPTED_FOR_VERTICAL_SLICE may proceed to Stage 6
  └── FAIL: Requirements BLOCKED or downgraded to DEFERRED

STAGE 6: DEC-034 Independent Verification (AUTHORITY: ESTABLISHED)
  ├── Separate session IV of the entire requirements system
  ├── Verifies: verifier review legitimacy, source grounding, no overclaiming,
  │            traceability validity, test mapping believability
  ├── PASS: GENERATED_REQUIREMENTS_AUTHORITY: ESTABLISHED
  └── FAIL: Requirements returned to Stage 5 for remediation

STAGE 7: Authoritative State (AUTHORITY: IMPLEMENTATION-READY)
  ├── All ACCEPTED_FOR_VERTICAL_SLICE requirements are authoritative
  ├── Recorded in: verifier-review.yaml implementation_authorization.status = AUTHORIZED
  ├── Implementation sprint may consume ACCEPTED_FOR_VERTICAL_SLICE IDs
  ├── Deferred requirements remain deferred — cannot be consumed without re-entering Stage 2
  └── NEEDS_REVIEW requirements: blocked from implementation
```

---

## Section 2: Where Authority Begins

| Stage | What changes | Authority level |
|-------|-------------|-----------------|
| Stage 0 | Human product goals defined | HUMAN (highest) |
| Stage 1 | Upstream sources confirmed | SPEC/EXISTING_SOURCE/VERIFIED_FACT |
| Stage 2 | AI synthesis | AI_PROPOSAL (lowest) |
| Stage 3 | Generated YAML files created | PROPOSAL |
| Stage 4 | Schema validation PASS | STRUCTURALLY VALID (not yet authoritative) |
| Stage 5 | Verifier review PASS | CONDITIONALLY ACCEPTED |
| Stage 6 | DEC-034 IV PASS | **AUTHORITATIVE** |
| Stage 7 | Implementation consumes IDs | IMPLEMENTATION-READY |

**Authority begins at Stage 6.** Prior stages produce proposals and validated proposals.

---

## Section 3: Authoritative Artifacts (Current State)

### FODS — Authority Status: ESTABLISHED

| Artifact | Location | Authority Status |
|----------|----------|-----------------|
| commercial-requirements.yaml | `generated-requirements/fods/` | AUTHORITATIVE (20 ACCEPTED_FOR_VERTICAL_SLICE) |
| object-model-requirements.yaml | `generated-requirements/fods/` | AUTHORITATIVE (5 entities, all ACCEPTED) |
| save-edit-requirements.yaml | `generated-requirements/fods/` | AUTHORITATIVE (ACCEPTED_FOR_VERTICAL_SLICE) |
| conversion-requirements.yaml | `generated-requirements/fods/` | AUTHORITATIVE (all future-scoped — correctly deferred) |
| traceability-map.yaml | `generated-requirements/fods/` | AUTHORITATIVE (5 product goals mapped) |
| verifier-review.yaml | `generated-requirements/fods/` | AUTHORITATIVE (LANE_R5_PASS) |

### FODT — Authority Status: ESTABLISHED

| Artifact | Location | Authority Status |
|----------|----------|-----------------|
| All 6 files | `generated-requirements/fodt/` | AUTHORITATIVE (LANE_R5_PASS + DEC-034 IV PASS) |
| FODT-REQ-040 (iterative traversal) | commercial-requirements.yaml | AUTHORITATIVE — critical_requirements map populated |

---

## Section 4: Advisory-Only Artifacts

These artifacts exist in the authority chain but are advisory, not authoritative:

| Artifact | Advisory role | Cannot be used to |
|----------|--------------|-------------------|
| generation-report.md | Human-readable generation summary | Override requirements YAML |
| AI synthesis notes (embedded in source_evidence) | Traceability context | Replace spec citations |
| Conway plan (flickering-tumbling-conway.md) | Skill system roadmap | Govern implementation directly |

---

## Section 5: AI_PROPOSAL-Only Artifacts

Requirements that remain at AI_PROPOSAL status and cannot drive implementation:

For FODS:
- **FODS-REQ-040** (typed cell values): status=NEEDS_REVIEW — not yet ACCEPTED
- **FODS-REQ-041** (row/column repeat expansion): status=NEEDS_REVIEW — not yet audited
- **FODS-CONV-001..004** (export/conversion): status=GENERATED — future sprint only

For FODT:
- **FODT-CONV-001..004** (export/conversion): status=GENERATED — future sprint only

**Any attempt to implement these without re-running Stages 2-6 is a governance violation.**

---

## Section 6: Gaps in Authority Formalization

The following aspects of the authority chain lack formal enforcement:

### Gap 1: Traceability-map and verifier-review schemas missing

These two YAML files are unvalidated by schema. An agent could corrupt them without detection.

| Impact | Severity |
|--------|----------|
| Traceability-map could have invalid product goal coverage | MEDIUM |
| Verifier-review could have malformed decisions | HIGH |
| Silent corruption would not be caught by validator | HIGH |

**Recommendation:** Add schemas in next tooling sprint. Priority: HIGH.

### Gap 2: No stale-detection code

The authority chain at Stage 4+ assumes requirements are current. If input sources change (new source code, updated acquisition pack), requirements become stale. No automated check prevents implementation from consuming stale requirements.

**Recommendation:** Add `--check-stale` flag to validator. Priority: MEDIUM.

### Gap 3: No cross-file consistency check

traceability-map.yaml `accepted_for_vertical_slice` list should match `ACCEPTED_FOR_VERTICAL_SLICE` entries in commercial-requirements.yaml. No automated check enforces this.

**Recommendation:** Add cross-file consistency check in validator. Priority: MEDIUM.

### Gap 4: No prompt quality gate

Conway's Phase 6 planned a 10-criterion prompt quality gate for generated implementation prompts. This gate does not exist. Generated prompts (ad hoc today) are not checked for forbidden git commands, gate overclaiming, or 20-component completeness.

**Recommendation:** Highest-value missing component for Conway Phase 6. Priority: HIGH for autonomous operation.

### Gap 5: No AI usage ledger integration

AGENTS.md H5 requires LLM calls to be logged in `.local/llm-logs/`. The requirements generation pipeline does not currently emit a JSONL log entry. TC-0053 has this as a deferred item.

**Recommendation:** Add ledger emit when generator is built as a standalone tool. Priority: LOW (manual compliance currently).

---

## Section 7: Authority Chain vs Conway Plan Comparison

| Authority chain element | Conway v2.0 planned | Actual state |
|------------------------|---------------------|-------------|
| AI_PROPOSAL status for generated output | YES | YES |
| Schema validation gate | YES | PARTIAL (4/6 schemas) |
| Verifier review (LANE-R5) | YES | COMPLETE for FODS/FODT |
| DEC-034 IV of requirements | IMPLIED (not explicit) | COMPLETE and now EXPLICIT in AGENTS.md AF13 |
| Implementation authorization | After verifier review | After verifier review + DEC-034 IV (STRONGER) |
| Stale detection | YES (planned in generator) | DOCUMENTED only, not coded |
| Cross-file consistency | YES (planned in validator) | NOT IMPLEMENTED |
| Prompt quality gate | YES (planned in Phase 6) | NOT IMPLEMENTED |

**The actual authority chain is STRONGER than Conway planned in one dimension (DEC-034 IV is now mandatory).** The actual implementation is WEAKER in three dimensions (2 missing schemas, no stale code, no prompt quality gate).

---

## Section 8: GENERATED_REQUIREMENTS_AUTHORITY Chain Status

**Current status (as of this sprint):**

- **FODS:** ESTABLISHED — all 6 stages passed; 20 requirements AUTHORITATIVE
- **FODT:** ESTABLISHED — all 6 stages passed; 20 requirements AUTHORITATIVE

**What "established" means:**
- Implementation sprints MAY consume ACCEPTED_FOR_VERTICAL_SLICE requirement IDs
- The Conway skill system MUST reference these IDs in generated prompts
- Future format additions MUST pass through all 6 stages before authority is established
- NEEDS_REVIEW and GENERATED requirements remain proposals until re-processed

**GENERATED_REQUIREMENTS_AUTHORITY_CHAIN: FULLY MAPPED**
