---
artifact_id: TC-0018-fods-gate4-parser-prototype-verification
artifact_type: taskcard
path: taskcards/TC-0018-fods-gate4-parser-prototype-verification.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 parser prototype DEC-034 independent verification taskcard for FODS. Created run028 (2026-05-05). Updated run029: TC-0017 executed (PASS 4/4) — TC-0018 now ready_for_execution. BLOCKED by explicit DEC-034 verification prompt (human must issue TC-0018 verification prompt in a new session)."
---

# TC-0018: FODS Gate 4 — Parser Prototype Independent Verification

**Taskcard ID:** TC-0018
**Phase:** 3 (Gate 4 verification — DEC-034 sprint)
**Gate:** Gate 4 (Parser Prototype)
**Status:** ready_for_execution
**Created:** 2026-05-05 (run028)
**Created by:** claude-sonnet-4-6 (run028)
**Blocking:** Gate 4 human approval
**Blocked by:** TC-0017 execution + explicit DEC-034 verification prompt

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0017 (Gate 4 parser prototype execution) is complete.
2. A human issues an explicit TC-0018 verification execution prompt.

Per DEC-034 and AGENTS.md Section V: independent agent verification must be performed in a separate execution session before Gate 4 is submitted for human approval.

---

## Objective

Perform an independent DEC-034 verification sprint on the Gate 4 parser prototype. Verify all TC-0017 claims before requesting Gate 4 human approval.

**Gate 4 is a human-only approval.** No agent may self-approve Gate 4.

---

## Prerequisites

- [ ] TC-0017 execution complete — `prototypes/by-format/fods/fods_parser.py` produced
- [ ] `acquisition-packs/fods/parser-notes.md` produced
- [ ] Registry `gate_4.status` = `prototype_created_pending_independent_verification`
- [ ] Explicit TC-0018 verification execution prompt issued by human

---

## Scope

### In scope

1. Independently re-run the prototype against all 4 Gate 3 samples
2. Verify PT-001 through PT-004 pass criteria without relying on TC-0017 run records
3. Verify `parser-notes.md` exists and is substantive (design decisions, security baseline documented)
4. Verify no forbidden paths were created (no `src/`, no `schemas/neutral-model/`, no product code)
5. Verify no Gate 4 self-approval occurred
6. Verify registry gate_4 status is `prototype_created_pending_independent_verification` (not `passed`)
7. Produce DEC-034 verification evidence bundle
8. Request Gate 4 human review

### Out of scope — FORBIDDEN

- Gate 4 self-approval — FORBIDDEN (human-only)
- Parser changes during verification — FORBIDDEN (read-only verification sprint)
- Product source creation — FORBIDDEN
- Oracle comparison — FORBIDDEN (Gate 6)

---

## Steps (to be executed when explicit TC-0018 prompt issued)

1. Read `AGENTS.md` Section V (independent verification rules).
2. Read TC-0017 completion record and `plans/master-plan.md`.
3. Independently run `prototypes/by-format/fods/fods_parser.py` against all 4 samples.
4. Record actual output; compare against `parser-test-plan.md` expected values.
5. Verify `parser-notes.md` exists and documents security baseline.
6. Check no forbidden paths were created.
7. Check registry gate_4.status is NOT `passed` (agent cannot set this).
8. Produce verification report.
9. Update registry gate_4 evidence_verified_by field.
10. Produce DEC-034 evidence bundle.
11. Request Gate 4 human approval.

---

## Acceptance Criteria

- [ ] PT-001 through PT-004 independently re-verified PASS
- [ ] `parser-notes.md` substantive (design decisions + security baseline)
- [ ] No forbidden paths created
- [ ] No Gate 4 self-approval in TC-0017 history
- [ ] Registry gate_4.status confirmed = `prototype_created_pending_independent_verification`
- [ ] DEC-034 verification evidence bundle produced
- [ ] Gate 4 human approval requested (but NOT granted by agent)

---

## Related Files

- `prototypes/by-format/fods/fods_parser.py` — prototype (TC-0017 deliverable)
- `acquisition-packs/fods/parser-notes.md` — parser design notes (TC-0017 deliverable)
- `acquisition-packs/fods/parser-test-plan.md` — expected parse output (this verification's oracle)
- `samples/by-format/fods/` — 4 Gate 3 samples with SHA-256 hashes
- `taskcards/TC-0017-fods-gate4-parser-prototype-execution.md` — execution parent
