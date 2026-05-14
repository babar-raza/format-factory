---
document_type: rollout_readiness_report
sprint: CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
title: "Autonomous Rollout Readiness Assessment"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Autonomous Rollout Readiness Assessment

**Sprint:** CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
**Date:** 2026-05-13

---

## Overall Verdict

| Component | Verdict |
|-----------|---------|
| Generalized /commercial-sprint | NOT_READY |
| Automatic implementation generation | NOT_READY |
| Autonomous requirements regeneration | NOT_READY |
| Vector retrieval deferral | CORRECT — remains deferred |
| Lexical retrieval sufficiency | SAFE_WITH_LIMITATIONS |
| Stale-detection gap impact | BLOCKING autonomous regeneration |
| Evidence contracts for autonomous scaling | SAFE_WITH_LIMITATIONS |
| Delegated gate authority | NOT_DELEGATED (correct) |

**AUTONOMOUS_ROLLOUT_READINESS: NOT_READY**

This does not mean Phase 2 cannot proceed. It means fully autonomous operation without human checkpoints is not safe yet. Human-reviewed prompt generation (Phase R4+) is safe.

---

## Section 1: Is Generalized /commercial-sprint Safe Yet?

**Verdict: NOT_READY**

Reasons:
1. `/commercial-sprint` command file does not exist
2. Format context resolver does not exist — no automated detection of REQUIREMENTS_AUTHORITATIVE state
3. No prompt quality gate — generated prompts not checked for forbidden git commands or gate overclaiming
4. State machine not implemented — sprint cannot detect that FODS/FODT are already in REQUIREMENTS_AUTHORITATIVE state and route correctly

What needs to exist for SAFE_WITH_LIMITATIONS:
- [ ] Format context resolver (Phase R2)
- [ ] Lane library (Phase R3)
- [ ] Prompt generator with quality gate (Phase R4)
- [ ] `/commercial-sprint` command (Phase R6)
- [ ] Test suite passes (Phase R7)
- [ ] Human review of generated prompts (Phase R7) — NOT automated

Even after all phases, a human checkpoint before execution remains mandatory. The skill system generates prompts for human review; it does not autonomously execute implementation.

---

## Section 2: Is Automatic Implementation Generation Safe Yet?

**Verdict: NOT_READY**

Reasons:
1. No prompt generator exists yet
2. No quality gate to validate generated prompts
3. Prompts for FODS/FODT would need to:
   - Reference ACCEPTED_FOR_VERTICAL_SLICE IDs (20 FODS + 20 FODT) — verified, but not automatically wired
   - Explicitly enforce FODT-REQ-040 iterative list traversal (non-negotiable safety constraint)
   - Not include NEEDS_REVIEW requirement IDs
   - Not claim Gate 11 passage
4. Without quality gate, generated prompts could contain forbidden content

Safest current path: Ad hoc implementation prompt, manually crafted by an agent reading the verifier-review.yaml and traceability-map.yaml files. This is what the next implementation sprint should do.

What changes the verdict:
- Phase R4 (prompt generator + quality gate) implemented and tested → SAFE_WITH_LIMITATIONS
- Quality gate must reject all 10 forbidden patterns before a generated prompt is emitted

---

## Section 3: Is Autonomous Requirements Regeneration Safe Yet?

**Verdict: NOT_READY**

Reasons:
1. No `generate_format_requirements.py` tool exists (needed for new formats)
2. No stale-detection code — regeneration can silently use outdated inputs
3. No cross-file consistency check — regeneration could produce traceability-map mismatched to commercial-requirements
4. For FODS/FODT specifically: requirements are already AUTHORITATIVE — regeneration without human authorization would be a governance violation (GOVERNANCE.md 26.11: stale requirements must be regenerated before use, but regeneration itself requires human authorization for established formats)

What changes the verdict:
- Phase R1: Add stale-detection code to validator
- Phase R3: Requirements generator tool built and tested
- Governance rule: regeneration for AUTHORITATIVE formats requires explicit human authorization taskcard
- IV checkpoint: regenerated requirements must go through Stages 4-6 again before authority is re-established

Current safe behavior: FODS/FODT requirements are authoritative; do not regenerate unless an input source changes. If input source changes, file a taskcard before regenerating.

---

## Section 4: Is Vector Retrieval Still Correctly Deferred?

**Verdict: CORRECT — remains deferred**

Reasons supporting continued deferral:
1. Requirements are already generated for FODS/FODT using lexical retrieval — regeneration not needed
2. ODF 1.3 spec is cached locally and well-structured; lexical section navigation is sufficient
3. Embedding infrastructure (LLM-001, EMB-001) is in backlog with no active taskcard
4. Adding vector retrieval before the skill system is built adds complexity without current benefit
5. docs/spec-retrieval-and-rag-policy.md guardrail: Tier 3 (vector/RAG) NOT authorized for gate evidence — further reason to defer

When to re-evaluate: When a new format requires spec navigation of a large, poorly-structured specification where lexical search produces too many false positives.

---

## Section 5: Is Lexical Retrieval Sufficient?

**Verdict: SAFE_WITH_LIMITATIONS**

Current use of lexical retrieval:
- Spec section navigation (grep over normalized spec text)
- Source file confirmation (path existence + class name search)
- Test file confirmation (path existence)
- Acquisition pack fact extraction (YAML key lookup)

For FODS/FODT: SUFFICIENT — all requirements were grounded using this approach with 0 AI_PROPOSAL accepted.

Limitations:
1. For formats with ambiguous spec structure (non-XML, complex encoding), lexical search may produce poor results
2. For deeply nested spec content, lexical retrieval may miss relevant sections
3. For cross-format reasoning (comparing FODS and FODT schema similarities), lexical retrieval is weaker

These limitations do not affect the current scope (FODS/FODT entity expansion, save improvements).

---

## Section 6: Are Stale-Detection Gaps Blocking Autonomy?

**Verdict: BLOCKING for autonomous regeneration; manageable for current scope**

Current state:
- input_source_hashes recorded in commercial-requirements.yaml (generation_timestamp: 2026-05-13)
- No automated comparison against current file hashes
- Manual check: compare source files against generation_timestamp

Impact analysis:
- FODS/FODT vertical slice: LOW RISK — requirements are authoritative; source not changing in this sprint
- Future entity expansion: MEDIUM RISK — when FodsCell is modified, FODS-REQ-013 may become stale
- New format entry: HIGH RISK — if acquisition pack changes between requirements generation and implementation

**What this means for Conway Phase R6 (commands):** The `/commercial-sprint` command MUST check stale status before emitting an implementation prompt. Without stale detection code, the command must fall back to a manual stale check instruction embedded in the generated prompt.

Practical mitigation until code is written:
- Every implementation sprint prompt must include: "Verify generation_timestamp in commercial-requirements.yaml against current source file dates. If any source file is newer, do not proceed — file a regeneration taskcard."

---

## Section 7: Are Evidence Contracts Strong Enough for Autonomous Scaling?

**Verdict: SAFE_WITH_LIMITATIONS**

Strong points:
- base-run.yaml v1.4 has floor of 30 metadata files
- RUN_CONTRACT_METADATA_FLOOR check prevents weakened contracts
- Auto-proof 3-pass build prevents placeholder proofs
- Forbidden path patterns prevent .git/, .local/, secrets

Limitations for autonomous scaling:
1. No semantic checks for "requirements artifacts present" — a contract could pass without including generated-requirements/ files
2. min_metadata_count floor of 30 is per-sprint; a large multi-format sprint would need a higher floor
3. No per-lane evidence isolation — all lanes contribute to one bundle
4. No verifier-review.yaml hash check — contracts do not verify that verifier-review matches what was reviewed

What must be added (Phase R5):
- `commercial-sprint-template.yaml` contract with semantic checks:
  - requirements_schema_validation_result: PASS required
  - verifier_review_present: required
  - iv_status: ESTABLISHED required
  - accepted_requirement_ids_referenced: at least 1 required
  - no_stale_requirements: manual attestation until automation exists

---

## Section 8: Is Delegated Gate Authority Sufficient?

**Verdict: NOT_DELEGATED (this is correct)**

Gate authority is not delegated to AI:
- All 11 gates require Babar Raza explicit human approval (AGENTS.md non-negotiable rule)
- AI may conduct DEC-034 IV (verification) but not gate approval
- Generated prompts must not contain gate self-approval language (quality gate criterion 3)
- Conway skill system explicitly prohibits gate self-approval (plan Section 23, rule 3)

This is not a gap — it is a correct governance boundary. The Conway skill system generates prompts and evidence for human review; it does not approve gates.

The only concern is that a poorly-written generated prompt might contain subtle gate overclaiming. The prompt quality gate (Phase R4) must explicitly check for this.

---

## Section 9: Readiness Summary Table

| Capability | Status | What's missing |
|-----------|--------|---------------|
| FODS/FODT requirements authoritative | READY | Nothing — COMPLETE |
| Requirements validation (4 schemas) | SAFE_WITH_LIMITATIONS | 2 missing schemas |
| Format context resolver | NOT_READY | Phase R2 not started |
| Lane library | NOT_READY | Phase R3 not started |
| Prompt generator | NOT_READY | Phase R4 not started |
| Prompt quality gate | NOT_READY | Phase R4 not started |
| Evidence contract template | NOT_READY | Phase R5 not started |
| /commercial-sprint command | NOT_READY | Phase R6 not started |
| Stale detection code | NOT_READY | TC-0053 deferred item |
| Full test suite | PARTIAL | pytest/jsonschema not installed |
| Gate approval | CORRECT — not delegated | Nothing to fix |

---

## Final Verdict

**AUTONOMOUS_ROLLOUT_READINESS: NOT_READY**

This means:
- Do NOT attempt to run /commercial-sprint autonomously — command does not exist
- Do NOT attempt autonomous requirements regeneration — would bypass stale-detection rule
- DO proceed with Phase R1 (schema hardening) as the next step
- DO use ACCEPTED_FOR_VERTICAL_SLICE requirement IDs in the next manual implementation sprint

The path to SAFE_WITH_LIMITATIONS requires completing Phases R1-R7 with human checkpoints at R6 and R7.
Full autonomous operation (SAFE_NOW) is not a target for this roadmap — human review of generated prompts remains mandatory.
