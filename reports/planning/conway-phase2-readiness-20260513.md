---
document_type: architecture_readiness_report
sprint: GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001
title: "Conway Phase 2 Readiness Assessment"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Conway Phase 2 Readiness Assessment

**Sprint:** GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001
**Date:** 2026-05-13

---

## Verdict

**CONWAY_PHASE2_READINESS: GO_WITH_LIMITATIONS**

Conway Phase 2 (generalized /commercial-sprint architecture) may proceed, with specific limitations
that must be respected. The generated-requirements architecture is mature enough for near-term
implementation of the already-accepted vertical slice requirements. It is not yet ready for
fully autonomous multi-format expansion.

---

## Section 1: Generated Requirements Architecture Maturity

| Dimension | Assessment | Score |
|-----------|-----------|-------|
| Schema coverage | 4 schemas (commercial, object-model, save-edit, conversion) | SUFFICIENT |
| Schema enforcement | manual_validate fallback operational; jsonschema absent | PARTIAL |
| Source grounding | 0 AI_PROPOSAL, 6 source types, all verified | STRONG |
| Verifier review system | verifier-review.yaml structure established; per-format | STRONG |
| Pipeline documentation | docs/ai-generated-format-requirements-pipeline.md present | STRONG |
| Traceability model | 5 product goals, critical_requirements map, deferred tracking | STRONG |
| Authority chain | Now formally documented (this sprint) | STRONG |

**Architecture maturity: SUFFICIENT for near-term use**

The architecture is not at Level 5 (fully autonomous), but at Level 3 (governed with human checkpoints). This is appropriate for Phase 3+ work.

---

## Section 2: Traceability Strength

| Dimension | Assessment |
|-----------|-----------|
| Product goal coverage | 5 PGs per format; all addressed at correct scope levels |
| Requirement-to-source mapping | Every requirement has source_evidence |
| Spec citations | Valid ODF 1.3 sections; no fabricated references |
| Critical requirements flagged | FODT-REQ-040 in critical_requirements map |
| Deferred clearly separated | NEEDS_REVIEW and future-scoped clearly distinguished from ACCEPTED |
| Test requirement coverage | All ACCEPTED_FOR_VERTICAL_SLICE have test_requirements |
| Cross-format consistency | FODS/FODT use identical schema structure |

**Traceability strength: STRONG for current scope**

Limitation: No cross-requirement dependency graph (e.g., FODS-CONV-001 depends on FODS-REQ-030 is documented in prose but not machine-verifiable). This is acceptable for Phase 2 but should be added before Phase 3 expansion.

---

## Section 3: Schema Rules Sufficiency

Current schemas enforce:
- Required top-level fields (format, spec_version, generator_version, etc.)
- Non-empty requirements array
- Unique requirement IDs
- AI_PROPOSAL cannot be ACCEPTED without verifier
- ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements
- Non-PRODUCT_DECISION requires source_evidence
- Conversion requirements cannot be ACCEPTED_FOR_VERTICAL_SLICE in initial sprint

**Gaps in schemas:**
1. No automated stale-detection against input_source_hashes
2. No cross-file consistency check (e.g., traceability-map accepted_for_vertical_slice must match commercial-requirements.yaml)
3. No verifier-review linkage check (verifier-review.yaml must review all ACCEPTED_FOR_VERTICAL_SLICE requirements)
4. jsonschema not installed — Draft7 validation falls back to manual_validate

**Schema sufficiency:** PARTIAL. Manual validation covers the most critical constraints. Missing cross-file consistency and stale-detection are operational risks, not blocking risks for the current known scope.

---

## Section 4: Evidence Contract Strength

The existing evidence contract system (base-run.yaml v1.3, tools/evidence/) is:
- Operationally confirmed PASS across 47+ sprints
- Sufficient for generated-requirements integration
- Missing: no specific "requirements regeneration" metadata requirement in the contract

**Recommendation:** Add a `requirements_schema_validation_result` field to evidence bundle metadata whenever a sprint regenerates or consumes generated requirements. This is a future enhancement, not a current blocker.

**Evidence contract strength: SUFFICIENT with noted gap**

---

## Section 5: Requirements Regeneration Trustworthiness

Regeneration is trustworthy IF:
1. Input sources are verified unchanged (currently manual)
2. Schema validation passes immediately after generation
3. Verifier review is conducted as a separate pass
4. DEC-034 IV is conducted before implementation consumes the output

**Current regeneration risk:** Without automated stale-detection, a regeneration sprint could silently use outdated input sources. This is mitigated by:
- input_source_hashes in each generated file (manual audit possible)
- TC-0053 Rule 1 documented stale-detection requirement
- Governance rule in GOVERNANCE.md 26.11 (added this sprint)

**Regeneration trustworthiness: CONDITIONAL** (trustworthy with manual stale check; fully trustworthy requires automated check)

---

## Section 6: Stale Detection Sufficiency

**Current state:**
- Stale-detection is DOCUMENTED (TC-0053 Rule 1, GOVERNANCE.md 26.11)
- Stale-detection is NOT AUTOMATED (no code in validator or separate tool)
- input_source_hashes fields are present in generated files (manual audit possible)

**Risk assessment:**
- For the current FODS and FODT vertical slice (no source changes since 2026-05-13): LOW RISK
- For future format expansion (new sources, different acquisition packs): MEDIUM RISK
- For autonomous regeneration without human review: HIGH RISK without automation

**Stale detection sufficiency: PARTIAL** — acceptable for Phase 2 with manual verification; must be automated before fully autonomous regeneration.

---

## Section 7: Lexical Retrieval Sufficiency

The current pipeline uses lexical retrieval (grep/search over local files) to ground requirements:
- Spec chunks from normalized spec text
- Source file exploration (src/net/ confirmation)
- Test file existence (tests/net/ confirmation)
- Acquisition pack facts (verified-facts.yaml, implementation-requirements.yaml)

**For near-term (Phase 2):** Lexical retrieval is SUFFICIENT.
- Known ODF structure means spec sections are predictable
- Existing source is confirmed, not inferred
- Test files are confirmed, not inferred

**For future expansion (new formats):** Lexical retrieval may become a bottleneck as format complexity increases. Vector/embedding retrieval would improve spec navigation but is not required now.

**Lexical retrieval sufficiency: SUFFICIENT for Phase 2**

---

## Section 8: Embeddings/Vector Retrieval Deferral

Should embeddings/vector retrieval remain deferred?

**YES — remain deferred for Phase 2.**

Reasons:
1. Current pipeline produces 0 AI_PROPOSAL requirements — retrieval quality is already satisfactory
2. ODF 1.3 spec is cached locally and well-structured; lexical section navigation works
3. Embedding infrastructure (llm.professionalize.com, models) is backlog (LLM-001, EMB-001 taskcards)
4. Adding vector retrieval now increases system complexity without current need
5. Phase 2 risk is implementation correctness, not retrieval quality

**Decision: Embeddings/vector retrieval stays deferred. Revisit when a new format is added where spec navigation becomes a bottleneck.**

---

## Section 9: Generalized /commercial-sprint Architecture Safety

The generalized /commercial-sprint architecture would automate:
1. Requirements validation check
2. Implementation prompt generation from accepted requirement IDs
3. Evidence bundle creation

**Safety assessment for Phase 2:**
- Requirements validation: SAFE (validator exists, runs standalone)
- Implementation prompt generation: CONDITIONAL (must reference only ACCEPTED_FOR_VERTICAL_SLICE IDs; must enforce non-negotiable rules from verifier-review.yaml)
- Autonomous implementation without human checkpoint: NOT SAFE YET

**Limitations for Phase 2:**
1. Stale-detection must run before any /commercial-sprint invocation
2. Critical constraints (e.g., FODT-REQ-040 iterative traversal) must be explicitly surfaced in the generated prompt
3. Human must review the generated implementation prompt before execution
4. No autonomous gate approval — gate approval remains human-only

**Generalized /commercial-sprint safety: CONDITIONAL** — safe with human prompt review; not safe for fully autonomous execution.

---

## Section 10: Conway Phase 2 Conditions

**GO_WITH_LIMITATIONS conditions:**

| Condition | Status | Notes |
|-----------|--------|-------|
| Use only ACCEPTED_FOR_VERTICAL_SLICE IDs | REQUIRED | Deferred/NEEDS_REVIEW IDs must not drive implementation |
| Enforce FODT-REQ-040 iterative constraint | REQUIRED | Any list traversal implementation must use Stack<T> |
| Manual stale check before regeneration | REQUIRED | Until automated check exists |
| Human review of generated prompt | REQUIRED | Before execution, not after |
| No Gate 11 approval in Phase 2 | REQUIRED | Gate 11 remains human-only |
| jsonschema installation | RECOMMENDED | Upgrade from manual_validate for stronger schema enforcement |
| pytest installation | RECOMMENDED | Enable full test suite execution |

**NOT GO conditions (if any of these are skipped, stop):**
- Attempting to use NEEDS_REVIEW or GENERATED requirements in implementation
- Bypassing verifier-review.yaml for new requirements
- Claiming Gate 11 passage based on Phase 2 vertical slice results
- Running /commercial-sprint autonomously without human checkpoint

---

## Final Verdict

**CONWAY_PHASE2_READINESS: GO_WITH_LIMITATIONS**

The generated-requirements system is mature enough to power Phase 2 implementation for the
already-verified FODS and FODT vertical slice requirements. All 40 accepted requirements (20 FODS,
20 FODT) are established as AUTHORITATIVE as of this sprint.

Phase 2 must respect the limitations above. Full autonomous expansion requires: (1) automated
stale detection, (2) jsonschema+pytest installation, (3) cross-file consistency checks.
These are Phase 3 prerequisites, not Phase 2 blockers.
