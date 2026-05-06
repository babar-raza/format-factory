---
artifact_id: TC-0024-fods-gate5-neutral-model-verification
artifact_type: taskcard
path: taskcards/TC-0024-fods-gate5-neutral-model-verification.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 5 neutral model DEC-034 independent verification taskcard for FODS. Created run033 (2026-05-06)."
---

# TC-0024: FODS Gate 5 — Neutral Model Independent Verification

**Taskcard ID:** TC-0024
**Phase:** 3 (Gate 5 verification — DEC-034 sprint)
**Gate:** Gate 5 (Neutral Model Defined)
**Status:** ready_for_execution
**Created:** 2026-05-06 (run033)
**Created by:** claude-opus-4-6 (run033)
**Blocking:** Gate 5 human approval
**Blocked by:** Explicit TC-0024 verification execution prompt from human

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0023 (Gate 5 neutral model execution) is complete.
2. A human issues an explicit TC-0024 verification execution prompt.

Per DEC-034 and AGENTS.md Section V: independent agent verification must be performed in a separate execution session before Gate 5 is submitted for human approval.

---

## Objective

Perform an independent DEC-034 verification sprint on the Gate 5 neutral model. Verify all TC-0023 claims before requesting Gate 5 human approval.

**Gate 5 is a human-only approval.** No agent may self-approve Gate 5.

---

## Prerequisites

- [ ] TC-0023 execution complete — neutral model files at `schemas/neutral-model/fods/` (run033)
- [ ] Registry `gate_5.status` = `neutral_model_created_pending_independent_verification`
- [ ] Explicit TC-0024 verification execution prompt issued by human

---

## Scope

### In scope

1. Independently re-run `tools/model/validate_neutral_model.py` against all 4 Gate 3 samples
2. Verify model.yaml defines all 6 entities with correct field types
3. Verify model.schema.json is valid JSON Schema and matches model.yaml
4. Verify field-map.yaml maps all prototype output fields to model entities
5. Verify coverage-matrix.yaml accurately reflects model capabilities
6. Verify validation-rules.yaml rules are consistent with model.yaml constraints
7. Verify no forbidden paths were created (no `src/`, no product code)
8. Verify no Gate 5 self-approval occurred
9. Verify registry gate_5 status is NOT `passed`
10. Produce DEC-034 verification evidence bundle
11. Request Gate 5 human review

### Out of scope — FORBIDDEN

- Gate 5 self-approval — FORBIDDEN (human-only)
- Model changes during verification — FORBIDDEN (read-only verification sprint)
- Product source creation — FORBIDDEN
- Oracle comparison — FORBIDDEN (Gate 6)

---

## Steps (to be executed when explicit TC-0024 prompt issued)

1. Read `AGENTS.md` Section V (independent verification rules).
2. Read TC-0023 completion record and `plans/master-plan.md`.
3. Independently run `tools/model/validate_neutral_model.py` against all 4 samples.
4. Verify model.yaml entity definitions (6 entities, field types, required flags).
5. Verify model.schema.json structural validity.
6. Verify field-map.yaml completeness (19 mappings documented).
7. Verify coverage-matrix.yaml totals (30 features: 13 covered, 2 partial, 10 deferred, 5 out-of-scope).
8. Verify validation-rules.yaml rule count (21 rules: 18 error, 3 warning).
9. Check no forbidden paths were created.
10. Check registry gate_5.status is NOT `passed`.
11. Produce verification report.
12. Update registry gate_5 evidence_verified_by field.
13. Produce DEC-034 evidence bundle.
14. Request Gate 5 human approval.

---

## Acceptance Criteria

- [ ] validate_neutral_model.py independently re-verified: 4/4 PASS
- [ ] model.yaml: 6 entities verified
- [ ] model.schema.json: valid JSON Schema, matches model.yaml
- [ ] field-map.yaml: 19 mappings verified
- [ ] coverage-matrix.yaml: 30 features, totals verified
- [ ] validation-rules.yaml: 21 rules verified
- [ ] No forbidden paths created
- [ ] No Gate 5 self-approval in run033 history
- [ ] Registry gate_5.status updated to `neutral_model_verified_pending_human_review`
- [ ] Gate 5 human approval requested (NOT granted by agent)

---

## Related Files

- `schemas/neutral-model/fods/model.yaml` — neutral model definition (TC-0023 deliverable)
- `schemas/neutral-model/fods/model.schema.json` — JSON Schema (TC-0023 deliverable)
- `schemas/neutral-model/fods/field-map.yaml` — prototype-to-model mapping (TC-0023 deliverable)
- `schemas/neutral-model/fods/coverage-matrix.yaml` — feature coverage (TC-0023 deliverable)
- `schemas/neutral-model/fods/validation-rules.yaml` — semantic rules (TC-0023 deliverable)
- `tools/model/validate_neutral_model.py` — validation tool (TC-0023 deliverable)
- `acquisition-packs/fods/neutral-model-notes.md` — design notes (TC-0023 deliverable)
- `taskcards/TC-0023-fods-gate5-neutral-model-execution.md` — execution parent
