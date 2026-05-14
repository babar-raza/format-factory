---
document_type: prior_sprint_dirty_tree_inventory
sprint: PRIOR-SPRINT-COMMIT-RECONCILIATION-AND-R4R5R6-RESUME-001
title: "Prior Sprint Dirty Tree Inventory"
date: "2026-05-13"
visibility: internal
---

# Prior Sprint Dirty Tree Inventory — 2026-05-13

**Sprint:** PRIOR-SPRINT-COMMIT-RECONCILIATION-AND-R4R5R6-RESUME-001

---

## Classification Summary

| Group | Sprint | Files | Status |
|-------|--------|-------|--------|
| G1 | FF-CURRENT-STATE-AND-AI-REQUIREMENTS-ALIGNMENT | 11 | CLEAN |
| G2 | ASSISTANT-SUPERVISION-METHODOLOGY-SYNC | 11 | CLEAN |
| G3 | GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION | 8 | CLEAN |
| G4 | CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM | 16 | CLEAN |
| G5 | CONWAY-R2R3-CONTEXT-AND-LANE-SELECTOR-SWARM | 10 | CLEAN |
| UNKNOWN | — | 0 | NONE |
| HELD | — | 0 | NONE |

---

## Group G1: FF-CURRENT-STATE-AND-AI-REQUIREMENTS-ALIGNMENT

Evidence: `tools/evidence/contracts/ff-current-state-alignment-20260513.yaml`

Files:
- `plans/master-plan.md` (v2.55)
- `docs/commercial-product-capability-model.md`
- `src/net/fods/README.md`
- `src/net/fodt/README.md`
- `reports/planning/autonomous-rollout-readiness-20260513.md`
- `reports/planning/conway-existing-infrastructure-audit-20260513.md`
- `reports/planning/conway-phase2-readiness-20260513.md`
- `reports/planning/conway-rebaseline-roadmap-20260513.md`
- `reports/planning/post-conway-rebaseline-next-sprint-20260513.md`
- `reports/governance/generated-requirements-governance-stabilization-20260513.md`
- `taskcards/TC-0053-ai-requirements-pipeline-governance.md`
- `tools/evidence/contracts/ff-current-state-alignment-20260513.yaml`
- `tools/evidence/contracts/conway-rebaseline-and-infrastructure-reconciliation-20260513.yaml`

Forbidden content check: CLEAN (no gate approval, no commercial_product_ready=true, no push)

---

## Group G2: ASSISTANT-SUPERVISION-METHODOLOGY-SYNC (CHATGPT-MEMORY-LOCAL-SYNC-20260513)

Evidence: `reports/governance/assistant-supervision-methodology-sync-20260513.md`

Files:
- `AGENTS.md` (AF15 added — ready-to-send prompts required)
- `GOVERNANCE.md` (26.13 added — supervision methodology reference)
- `docs/assistant-supervision-methodology.md` (new)
- `docs/assistant-supervision-methodology.yaml` (new)
- `docs/project-execution-standards.md` (new)
- `docs/project-execution-standards.yaml` (new)
- `memory/25-assistant-supervision-methodology-20260513.md` (new)
- `reports/governance/assistant-supervision-methodology-sync-20260513.md` (new)
- `reports/governance/assistant-supervision-methodology-sync-20260513.yaml` (new)
- `taskcards/ASSISTANT-SUPERVISION-METHODOLOGY.md` (new)
- `taskcards/PROJECT-EXECUTION-STANDARDS.md` (new)

Forbidden content check: CLEAN

---

## Group G3: GENERATED-REQUIREMENTS-DEC034-IV-AND-GOVERNANCE-STABILIZATION

Evidence: `tools/evidence/contracts/generated-requirements-dec034-iv-governance-stabilization-20260513.yaml`

Files:
- `generated-requirements/fods/object-model-requirements.yaml` (updated)
- `generated-requirements/fods/verifier-review.yaml` (updated)
- `generated-requirements/fodt/object-model-requirements.yaml` (updated)
- `reports/requirements/generated-requirements-authority-map-20260513.md`
- `reports/requirements/requirements-authority-iv-20260513.md`
- `reports/requirements/schema-hardening-report-20260513.md`
- `reports/requirements/validator-hardening-report-20260513.md`
- `tools/evidence/contracts/generated-requirements-dec034-iv-governance-stabilization-20260513.yaml`

Forbidden content check: CLEAN
AI_PROPOSAL count: 0 in all affected files (verified by validator)

---

## Group G4: CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM

Evidence: `tools/evidence/contracts/conway-r1r2-accelerated-foundation-swarm-20260513.yaml`

Files:
- `schemas/generated-requirements/traceability-map.schema.json` (new)
- `schemas/generated-requirements/verifier-review.schema.json` (new)
- `schemas/skills/format-config.schema.yaml` (new)
- `schemas/skills/skill-input.schema.yaml` (new)
- `tests/requirements/test_validate_generated_requirements.py` (updated — 32 tests)
- `tests/requirements/fixtures/` (9 fixture files — all validator test fixtures)
- `tools/requirements/validate_generated_requirements.py` (updated — 6-schema + cross-file)
- `templates/commercial-sprint/lane-library.yaml` (new)
- `templates/evidence/base-commercial-sprint.contract.yaml` (new)
- `reports/planning/context-resolver-scaffolding-20260513.md`
- `reports/planning/evidence-contract-template-model-20260513.md`
- `reports/planning/format-config-schema-scaffolding-20260513.md`
- `reports/planning/prompt-quality-gate-design-20260513.md`
- `reports/planning/r3-readiness-decision-20260513.md`
- `reports/testing/requirements-test-hardening-report-20260513.md`
- `reports/testing/requirements-tooling-environment-20260513.md`

Forbidden content check: CLEAN
No source mutations. No bin/obj. No gate approval.

---

## Group G5: CONWAY-R2R3-CONTEXT-AND-LANE-SELECTOR-SWARM

Evidence: `tools/evidence/contracts/conway-r2r3-context-and-lane-selector-swarm-20260513.yaml`

Files:
- `registry/format-registry.yaml` (generated_requirements block added for FODS+FODT)
- `tools/skills/format_context_resolver.py` (registry iv_status fallback added)
- `tools/skills/lane_selector.py` (new — deterministic lane selection)
- `tests/skills/test_format_context_resolver.py` (new — 26 tests)
- `tests/skills/test_lane_selector.py` (new — 24 tests)
- `reports/planning/r2-authority-state-completion-20260513.md`
- `reports/planning/lane-library-consistency-review-20260513.md`
- `reports/planning/evidence-bundle-size-containment-20260513.md`
- `reports/planning/r4-readiness-decision-20260513.md`
- `tools/evidence/contracts/conway-r2r3-context-and-lane-selector-swarm-20260513.yaml`

Forbidden content check: CLEAN
commercial_product_ready: false (unchanged)
gate_11 status: commercial_readiness_in_progress (unchanged)

---

## Held Files: NONE

## Unknown Files: NONE

---

**INVENTORY_STATUS: COMPLETE**
**FORBIDDEN_CONTENT_VIOLATIONS: 0**
**UNKNOWN_FILES: 0**
**HELD_FOR_INVESTIGATION: 0**
**PROCEED_TO_COMMIT: YES**
