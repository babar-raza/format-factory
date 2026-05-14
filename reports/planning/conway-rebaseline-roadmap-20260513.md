---
document_type: rebaseline_roadmap
sprint: CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
title: "Conway Rebaseline Roadmap"
date: "2026-05-13"
base_plan: "C:\\Users\\prora\\.claude\\plans\\flickering-tumbling-conway.md (v2.0)"
visibility: internal
publish_allowed: false
---

# Conway Rebaseline Roadmap

**Sprint:** CONWAY-REBASELINE-AND-INFRASTRUCTURE-RECONCILIATION-001
**Date:** 2026-05-13
**Base plan:** flickering-tumbling-conway.md v2.0 (14 phases)

---

## Section 1: What Has Changed Since Conway v2.0

Conway v2.0 was written on 2026-05-13 as a plan document. Within the same sprint window:

1. **Generated requirements were produced** — FODS/FODT requirements generated as Lane R3/R4 within COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
2. **Verifier reviews were completed** — LANE_R5_PASS for both formats
3. **DEC-034 IV was completed** — GENERATED_REQUIREMENTS_AUTHORITY: ESTABLISHED
4. **TC-0053 was completed** — governance contract finalized
5. **AGENTS.md AF13 was extended** — authority chain explicitly documented
6. **GOVERNANCE.md 26.11 was extended** — stale-detection rule, pipeline reference added

**Conway v2.0 was written before these events. It must be rebased against the new reality.**

---

## Section 2: Revised Phase Status

| Original phase | Original description | Revised status |
|----------------|---------------------|---------------|
| Phase 1 | Plan Repair | COMPLETE — flickering-tumbling-conway.md v2.0 |
| Phase 2 | Schemas and Validator | PARTIAL — 4/6 schemas, validator, tests (no fixtures) |
| Phase 3 | Requirements Generator and Verifier Tools | OBSOLETE FOR FODS/FODT; NEEDED FOR FUTURE FORMATS |
| Phase 4 | Format Context Resolver Upgrade | NOT STARTED |
| Phase 5 | Lane Library with R-Lanes | NOT STARTED — HIGHEST VALUE |
| Phase 6 | Prompt Generator Upgrade | NOT STARTED |
| Phase 7 | Evidence Contract Generator | MERGE WITH PHASE 2 — use template, not new tool |
| Phase 8 | Commands | NOT STARTED |
| Phase 9 | Golden Fixtures for FODS/FODT | SUPERSEDED — real outputs ARE the golden fixtures |
| Phase 10 | Skill System Tests | NOT STARTED |
| Phase 11 | Dry-run /commercial-sprint FODS | NOT STARTED |
| Phase 12 | Dry-run /commercial-sprint FODT | NOT STARTED |
| Phase 13 | IV of Skill System | NOT STARTED |
| Phase 14 | Controlled Rollout to Next Format | NOT STARTED |

---

## Section 3: Revised Phases (Rebased)

### Phase R0: COMPLETED — Requirements Authority Established (THIS SPRINT)

**Status:** COMPLETE
**Artifacts:**
- generated-requirements/fods/ (7 files, AUTHORITATIVE)
- generated-requirements/fodt/ (7 files, AUTHORITATIVE)
- DEC-034 IV: PASS (GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION-001)
- AGENTS.md AF13 updated
- GOVERNANCE.md 26.11 updated
- TC-0053: COMPLETED

**Authority checkpoint:** GENERATED_REQUIREMENTS_AUTHORITY: ESTABLISHED for FODS + FODT

---

### Phase R1: Schema and Tooling Hardening

**Status:** NEXT (recommended sprint)
**Scope:**
1. Add `schemas/generated-requirements/traceability-map.schema.json`
2. Add `schemas/generated-requirements/verifier-review.schema.json`
3. Add `tests/requirements/fixtures/` (4 fixture files: valid, duplicate-ids, ai-only-accepted, conversion-not-scoped)
4. Install pytest and jsonschema in active Python environment
5. Confirm `python -m pytest tests/requirements -v` → 9/9 PASS
6. Add stale-detection `--check-stale` flag to validator (optional — may defer to separate sprint)

**Does NOT include:**
- Command files
- tools/skills/ tools
- templates/
- Any implementation of commercial capabilities

**Authority checkpoint:** All 6 schemas present; full test suite passes; validator covers all 6 files

---

### Phase R2: Format Config Schema + Context Resolver

**Status:** NOT STARTED — depends on Phase R1
**Scope:**
1. Create `schemas/skills/format-config.schema.yaml` (defines format-specific class names, paths, build commands)
2. Create `schemas/skills/format-context-output.schema.yaml` (output block from context resolver)
3. Create `tools/skills/format_context_resolver.py` (reads registry, pack.yaml, neutral model, src/net/, generated-requirements/)
4. Create `tests/skills/test_format_context_resolver.py` with FODS and FODT golden fixture tests
5. Create `tests/skills/fixtures/fods-context.json` and `fodt-context.json`

**Dependency:** Phase R1 (schemas environment must be clean before adding skills)

**State machine output:** Resolver must return one of:
- REQUIREMENTS_MISSING — triggers requirements generation
- REQUIREMENTS_GENERATED_UNVERIFIED — triggers verifier pass
- REQUIREMENTS_VERIFIED_NO_IV — triggers DEC-034 IV
- REQUIREMENTS_AUTHORITATIVE — ready for implementation prompt
- BLOCKED (with reason: Gate not passed, DEC-033 unresolved, etc.)

**Authority checkpoint:** Context resolver correctly identifies FODS/FODT as REQUIREMENTS_AUTHORITATIVE

---

### Phase R3: Lane Library

**Status:** NOT STARTED — depends on Phase R2
**Scope:**
1. Create `templates/commercial-sprint/lane-library.yaml` (R-lanes + I-lanes + C-lanes)
2. Create `tools/skills/lane_selector.py` (selects lanes based on capability target and format state)
3. Create `tests/skills/test_lane_selector.py`

**Lane library must include:**
- LANE-R3: Requirements generation (AI synthesis from local sources)
- LANE-R4: Format context resolver (reads all per-format data)
- LANE-R5: Verifier review (adversarial challenge)
- LANE-C: Coordinator (integration, evidence, state update)
- I-LANES: Implementation lanes (by entity type — Load, Object Model, Edit, Save, Tests, AI Governance)
- LANE-K: AI orchestration (per docs/agent-swarm-ai-orchestration.md)

**Critical:** Lane library must explicitly include FODT-REQ-040 iterative traversal constraint in the I-lanes for list entities. This constraint must surface in every generated FODT implementation prompt.

**Authority checkpoint:** lane_selector.py tested with FODS/FODT context → correct lane set returned

---

### Phase R4: Prompt Generator with Quality Gate

**Status:** NOT STARTED — depends on Phase R3 (highest risk if skipped)
**Scope:**
1. Create `templates/commercial-sprint/coordinator-template.md` (20-component execution handoff)
2. Create `tools/skills/swarm_prompt_generator.py` (reads context, requirements, lanes → prompt)
3. Create `tools/skills/prompt_quality_gate.py` (10-criterion validation of generated prompts)
4. Create `tests/skills/test_swarm_prompt_generator.py`
5. Create `tests/skills/test_prompt_quality_gate.py`
6. Create `tests/skills/fixtures/fods-sprint-prompt.md` and `fodt-sprint-prompt.md`

**Quality gate criteria (10):**
1. No forbidden git commands (stash/reset/restore/clean/push)
2. No broad staging (add -A / add .)
3. No gate self-approval language
4. No commercial readiness claim
5. All 20 required prompt components present (per execution-handoff standard)
6. At least one ACCEPTED_FOR_VERTICAL_SLICE requirement ID referenced
7. No NEEDS_REVIEW or GENERATED requirement IDs referenced
8. Evidence contract path referenced
9. DEC-034 IV prompt referenced
10. No overclaim beyond current capability level

**Authority checkpoint:** Quality gate passes against FODS and FODT golden prompts

---

### Phase R5: Evidence Contract Template

**Status:** NOT STARTED — depends on Phase R4
**Scope:**
1. Create `tools/evidence/contracts/commercial-sprint-template.yaml` (inherits base-run; adds requirements semantic checks)
2. Contract semantic checks include: requirements_schema_validation_result, verifier_review_present, iv_status, accepted_requirement_ids_referenced, no_stale_requirements

**Merged with original Phase 7.** NOT a new evidence_contract_generator.py tool. A template that sprint coordinators instantiate.

---

### Phase R6: Commands (Phase 8 rebased)

**Status:** NOT STARTED — depends on Phases R2-R5
**Scope:** All 9 `.claude/commands/` skill files

Key behavioral changes from Conway v2.0:
1. `/commercial-sprint` state machine must handle REQUIREMENTS_AUTHORITATIVE state (FODS/FODT)
2. `/generate-format-requirements` must refuse to run if requirements already AUTHORITATIVE (stale check required)
3. All commands must begin with AUTHORITY header per plan Section 23
4. `/sprint-verify` must reference the stronger authority chain (verifier review + DEC-034 IV)

---

### Phase R7: Full Skill System Test Suite and FODS/FODT Dry-Run

**Status:** NOT STARTED — depends on Phase R6
**Merged from original phases 10, 11, 12.**
- Complete test suite (requirements + skills): run and confirm PASS
- Dry-run `/commercial-sprint fods` → generates FODS implementation prompt → human review
- Dry-run `/commercial-sprint fodt` → generates FODT implementation prompt → human review
- Both prompts reference: ACCEPTED_FOR_VERTICAL_SLICE requirement IDs, FODT-REQ-040 constraint, evidence contract path, DEC-034 IV path

---

### Phase R8: IV of Skill System (DEC-034)

**Status:** NOT STARTED — depends on Phase R7
**Original Phase 13 — unchanged.**
Separate session IV verifies:
- All schemas valid
- All tools runnable
- All tests pass
- Generated prompts meet quality gate
- No forbidden content
- State machine correctly identifies format readiness states

---

### Phase R9: First New Format Rollout

**Status:** NOT STARTED — depends on Phase R8
**Original Phase 14 — unchanged.**
First format added to registry after Gates 1-10.
Requirements generator tool (Conway Phase 3 / rebased as part of this phase) runs for the first time on a format where no requirements exist yet.

---

## Section 4: Phases to DELETE or MERGE

| Original phase | Action | Reason |
|----------------|--------|--------|
| Phase 9 (golden fixtures) | DELETE | Superseded — real FODS/FODT outputs are golden fixtures |
| Phase 7 (evidence_contract_generator.py tool) | MERGE into Phase R5 | Use template model, not a new generator tool |
| Phases 11+12 (dry-run separately) | MERGE into Phase R7 | Combine FODS/FODT dry-runs into one phase |

---

## Section 5: Dependency Graph

```
Phase R0 (COMPLETE)
  └── Phase R1 (schemas, tooling hardening)
        └── Phase R2 (format config schema + context resolver)
              └── Phase R3 (lane library)
                    └── Phase R4 (prompt generator + quality gate)
                          └── Phase R5 (evidence contract template)
                                └── Phase R6 (commands)
                                      └── Phase R7 (full tests + dry-runs)
                                            └── Phase R8 (IV of skill system)
                                                  └── Phase R9 (first new format)
```

Each phase is a strict blocker for all downstream phases. No phase may proceed without:
1. All tests passing for its scope
2. An evidence bundle validated
3. Human review (for Phase R6+ which adds commands)

---

## Section 6: Authority Checkpoints

| Phase | Authority checkpoint |
|-------|---------------------|
| R0 | GENERATED_REQUIREMENTS_AUTHORITY: ESTABLISHED (DONE) |
| R1 | SCHEMA_VALIDATION_COVERAGE: 6/6 schemas; test suite: 9/9 PASS |
| R2 | FORMAT_CONTEXT_RESOLVER: FODS→REQUIREMENTS_AUTHORITATIVE; FODT→REQUIREMENTS_AUTHORITATIVE |
| R3 | LANE_LIBRARY: FODS correct lane set; FODT iterative constraint in I-lanes |
| R4 | PROMPT_QUALITY_GATE: 10/10 criteria PASS for FODS and FODT golden prompts |
| R5 | EVIDENCE_CONTRACT_TEMPLATE: semantic checks include requirements artifacts |
| R6 | COMMANDS: all 9 present; AUTHORITY headers present; state machine handles AUTHORITATIVE state |
| R7 | FULL_TEST_SUITE: requirements + skills all PASS; dry-runs produce human-reviewable prompts |
| R8 | IV_OF_SKILL_SYSTEM: DEC-034 PASS (separate session) |
| R9 | FIRST_NEW_FORMAT: requirements generated, verified, IV'd via skill system |

---

## Section 7: Governance Checkpoints

| Phase | Governance checkpoint |
|-------|----------------------|
| R1 | pytest + jsonschema installed → no more manual_validate fallback |
| R2 | Context resolver output schema defined → no ambiguous context blobs |
| R4 | Prompt quality gate rejects forbidden git commands, gate overclaiming → safe autonomous generation |
| R6 | AUTHORITY headers in all commands → no command bypasses AGENTS.md/GOVERNANCE.md |
| R8 | DEC-034 IV of skill system → skill system output is authoritative |

---

## Section 8: Autonomous Rollout Checkpoints

Phases R1-R5: Human must review each phase's output before proceeding to next.
Phase R6 (commands): Human review of each generated command file.
Phase R7 (dry-runs): Human must review generated prompts for FODS and FODT before authorization.
Phase R8 (IV): Separate session — cannot be conducted by same session as Phase R7.
Phase R9 (new format): First rollout MUST have human checkpoint at each of: context check, requirements generation, verifier review, IV.

---

## Section 9: Mandatory IV Checkpoints

| Phase | IV type | Session requirement |
|-------|---------|---------------------|
| R0 | DEC-034 IV of requirements | COMPLETE (this sprint) |
| R1 | Schema validation run | Same session acceptable |
| R2 | Context resolver accuracy check | Same session acceptable |
| R3-R5 | Test suite PASS | Same session acceptable |
| R6 | Command file review | Human review required |
| R7 | Dry-run prompt review | Human review required |
| R8 | Full skill system DEC-034 IV | SEPARATE SESSION REQUIRED |
| R9 | New format requirements DEC-034 IV | SEPARATE SESSION REQUIRED |

---

## Section 10: What Must Be Abandoned

1. **Original Phase 9 (golden fixtures as separate phase):** ABANDONED — real FODS/FODT outputs serve this purpose
2. **Standalone `generation-metadata.yaml`:** ABANDONED — metadata embedded in commercial-requirements.yaml
3. **Separate `evidence_contract_generator.py` tool:** ABANDONED — use contract template inheritance
4. **Conway assumption that FODS/FODT are unprocessed:** ABANDONED — state machine must handle REQUIREMENTS_AUTHORITATIVE

## Section 11: What Becomes Future Work (Beyond Phase R9)

- Embeddings/vector retrieval for spec navigation (LLM-001, EMB-001 taskcards)
- Non-XML format support (REP-001, REP-003 taskcards)
- Non-Aspose registry expansion (NAC-001 taskcard)
- C9 (export/convert) capability development — requires conversion sprint
- Typed value extraction (FODS-REQ-040) — requires typed-value sprint
- Row/column repeat expansion (FODS-REQ-041) — requires audit + typed-value sprint

**CONWAY_REBASELINE_STATUS: COMPLETE**
