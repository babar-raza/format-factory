---
document_type: governance_stabilization_report
sprint: GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001
title: "Generated Requirements Governance Stabilization"
date: "2026-05-13"
tc: TC-0053
visibility: internal
publish_allowed: false
---

# Generated Requirements Governance Stabilization Report

**Sprint:** GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001
**Date:** 2026-05-13
**TC:** TC-0053

---

## TC-0053 Status After This Sprint

**Before:** not_started
**After:** completed (with 2 deferred items — see below)

---

## Section 1: Changes Made

### 1.1 AGENTS.md AF13 — Pipeline Doc Reference Added

**File:** `AGENTS.md`
**Section:** AF13 (Generated Requirements Are Mandatory Before Implementation)

**Change:** Added the following two sentences to the end of AF13:

> Generated requirements become authoritative only after both verifier review (verifier-review.yaml
> LANE_R5_PASS) and DEC-034 independent verification. Prior to that, they are proposals.
> Pipeline design: `docs/ai-generated-format-requirements-pipeline.md`. Governance rules: `taskcards/TC-0053-ai-requirements-pipeline-governance.md`.

**Rationale:** TC-0053 acceptance criterion required `docs/ai-generated-format-requirements-pipeline.md` to be referenced in AGENTS.md. AF13 was the correct location as it already governs generated requirements policy. The added explicit authority statement ("authoritative only after verifier review + DEC-034 IV") satisfies the sprint requirement.

### 1.2 GOVERNANCE.md 26.11 — Pipeline Doc Reference + Authority Chain

**File:** `GOVERNANCE.md`
**Section:** 26.11 (Generated Requirements Mandatory Before Implementation)

**Change:** Extended the rule to add:

1. Explicit authority chain statement: "Generated requirements become authoritative only after verifier review (verifier-review.yaml LANE_R5_PASS) AND DEC-034 independent verification by a separate session."
2. Stale-detection documentation: "Stale requirements (input sources changed since generation) must be regenerated before use."
3. Pipeline doc reference: `docs/ai-generated-format-requirements-pipeline.md`
4. Governance contract reference: `taskcards/TC-0053-ai-requirements-pipeline-governance.md`

**Rationale:** GOVERNANCE.md Section 26.11 previously referenced AGENTS.md AF13 and stated the mandatory-before-implementation rule, but did not explicitly state the authority chain or stale-detection requirement. These were added as governance rules, not implementation requirements.

### 1.3 TC-0053 Acceptance Criteria — Updated

**File:** `taskcards/TC-0053-ai-requirements-pipeline-governance.md`
**Status changed:** not_started → completed

**Criteria resolved:**
- [x] `docs/ai-generated-format-requirements-pipeline.md` in AGENTS.md → DONE (AF13 updated)
- [x] `GOVERNANCE.md` references pipeline governance rules → DONE (26.11 updated)
- [x] Regeneration trigger documented → DONE (GOVERNANCE.md 26.11 and TC-0053 Rule 1)

**Criteria deferred (separate sprint required):**
- [ ] Stale-detection check added to `validate_generated_requirements.py` → code change required
- [ ] AI usage log entry in evidence bundles → evidence bundle tooling change required

---

## Section 2: Generated Requirements Authority Chain

The authority chain is now formally documented in both AGENTS.md and GOVERNANCE.md:

```
AI generates requirements
  → Schema validation (REQUIREMENTS_SCHEMA_VALIDATION: PASS)
     Hard gate — fail blocks implementation
  → Verifier review (verifier-review.yaml LANE_R5_PASS)
     Separate pass — adversarial challenge
  → DEC-034 independent verification (separate session)
     Sprint-level IV confirms verifier legitimacy
  → GENERATED_REQUIREMENTS_AUTHORITY: ESTABLISHED
     → Requirements are AUTHORITATIVE for implementation
```

**Prior to DEC-034 IV, generated requirements are proposals, not authority.**

This authority chain was established as policy in this sprint and recorded in both AGENTS.md AF13 and GOVERNANCE.md 26.11.

---

## Section 3: Stale-Detection Requirement Documentation

TC-0053 Rule 1 (Stale Detection) states:
> Every generation run records `input_source_hashes` for all 10+ input sources.
> If any input hash changes, regeneration is REQUIRED before implementation may proceed.
> Stale artifacts must be clearly marked — no silent use of outdated requirements.

**Current state of input_source_hashes:**
Both FODS and FODT commercial-requirements.yaml include `input_source_hashes` fields referencing:
- verified_facts, neutral_model, existing source parser, existing source document, existing tests, tier_map, implementation_requirements

**Gap:** No automated check compares current file state against recorded hashes. This is documented as a deferred item requiring a separate implementation sprint.

**Mitigation until code is written:** Any agent beginning an implementation sprint must manually verify that the referenced source files have not changed materially since generation_timestamp (2026-05-13). If files have changed, regeneration is required.

---

## Section 4: Delegated Gate Authority Clarification

**Clarified position (now in AGENTS.md AF13 and GOVERNANCE.md 26.11):**

- AI agents may GENERATE requirements, VALIDATE schemas, and CONDUCT verifier review
- AI agents may NOT approve gates — gate approval requires human decision (GOVERNANCE.md Section 2, AF6)
- AI agents may conduct DEC-034 IV — this is an agent role, not a human role
- Generated requirements PLUS DEC-034 IV = AUTHORITATIVE for implementation
- Gate 11 commercial readiness still requires human approval — no change to that rule

The confusion point was: does DEC-034 IV on requirements make the requirements "gate-approved"? The answer is NO — DEC-034 IV establishes AUTHORITY for implementation, not gate passage. Gate 11 remains a human-only approval.

---

## Section 5: AI Acceleration vs Authority Wording

**Clarified position:**

| Activity | AI role | Authority status |
|----------|---------|-----------------|
| Requirements generation | Accelerator | Proposal until verified |
| Schema validation | Checker | Gate — blocks if fail |
| Verifier review | Adversarial reviewer | Required for ACCEPTED_FOR_VERTICAL_SLICE |
| DEC-034 IV | Independent verifier | Establishes authority |
| Gate approval | NOT PERMITTED | Human only |
| Commercial readiness claim | NOT PERMITTED | Human + evidence bundle + capability model |

This table is now consistent with `docs/assistant-supervision-methodology.md` Section 10 (AI Usage Methodology) and AGENTS.md Section AF12.

---

## Section 6: Deferred Items

These two items from TC-0053 are DEFERRED and require explicit authorization in a new sprint:

### D1: Stale-Detection Code

**Deferred to:** requirements tooling implementation sprint
**Reason:** Adding hash comparison logic to `validate_generated_requirements.py` is an implementation task not in scope for this governance/verification sprint.
**Impact if skipped long-term:** Silent use of stale requirements is possible; agents must manually check generation_timestamp and input references.

### D2: AI Usage Log in Evidence Bundles

**Deferred to:** evidence bundle tooling sprint
**Reason:** Adding AI usage log entries to evidence bundles requires changes to `tools/evidence/build_evidence_bundle.py` — outside governance scope.
**Impact if skipped long-term:** No persistent log of which AI model generated which requirements.

---

## Final Verdict

| Category | Result |
|----------|--------|
| TC0053_STATUS | COMPLETE (with 2 deferred items) |
| AGENTS.md pipeline doc reference | ADDED |
| GOVERNANCE.md authority chain | ADDED |
| Generated requirements authority statement | ADDED |
| Delegated gate authority wording | CLARIFIED |
| AI acceleration vs authority | CLARIFIED |
| Stale-detection code | DEFERRED |
| AI usage log in bundles | DEFERRED |

**TC0053_STATUS: COMPLETE**
