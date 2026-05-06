---
artifact_id: TC-0019-fods-gate5-neutral-model-planning
artifact_type: taskcard
path: taskcards/TC-0019-fods-gate5-neutral-model-planning.md
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
notes: "Gate 5 neutral model planning taskcard for FODS. Created run029 (2026-05-05). TC-0018 PASS (run030). TC-0021 quality review PASS (run031). Status: ready_for_execution_after_gate4_approval. Still blocked by Gate 4 human approval + explicit Gate 5 prompt. No schema creation yet. No neutral model yet."
---

# TC-0019: FODS Gate 5 — Neutral Model Planning

**Taskcard ID:** TC-0019
**Phase:** 3 (Gate 5 planning — future)
**Gate:** Gate 5 (Neutral Model)
**Status:** ready_for_execution_after_gate4_approval
**Created:** 2026-05-05 (run029)
**Created by:** claude-sonnet-4-6 (run029)
**Blocking:** Gate 5 execution
**Blocked by:** Gate 4 human approval (TC-0018 verification PASS run030) + explicit Gate 5 planning prompt

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0018 independent verification sprint (DEC-034) completes with PASS
2. Gate 4 is approved by a human (Babar Raza or equivalent)
3. A human issues an explicit Gate 5 planning prompt naming TC-0019

Current state (run029):
- Gate 4: prototype_created_pending_independent_verification
- Gate 4 approved: NO
- TC-0018: ready_for_execution (blocked by explicit DEC-034 prompt)
- Gate 5: not_started
- No neutral model schema exists
- No schemas/neutral-model/ directory

---

## Purpose

This taskcard governs the Gate 5 neutral model planning phase for FODS.

Gate 5 produces:
- A neutral intermediate model schema (`schemas/neutral-model/fods/`) defining the
  language-neutral representation of parsed FODS data
- Mapping tables from prototype JSON output → neutral model fields
- Design for future roundtrip (export) capability

Gate 5 is NOT product source. It is an evidence artifact that informs product development.

---

## Scope (planning only — out-of-scope items are FORBIDDEN now)

### Will be in scope (after Gate 4 passes and explicit prompt issued)

1. Define neutral model schema for FODS in `schemas/neutral-model/fods/`
2. Map prototype output (Gate 4 JSON) to neutral model fields
3. Document value type handling (float, string, boolean, date, formula-cached)
4. Document sheet/row/cell hierarchy mapping
5. Record limitations relative to full ODF 1.3 spec coverage

### Out of scope — FORBIDDEN (applies now and at Gate 5)

- Product source (`src/python/fods/`, `src/net/fods/`) — FORBIDDEN (Gate 9+)
- Gate 5 self-approval — FORBIDDEN (human-only)
- Oracle comparison — FORBIDDEN (Gate 6)
- Fuzz testing — FORBIDDEN (Gate 7)
- Security report — FORBIDDEN (Gate 8)
- CI workflows — FORBIDDEN (Gate 10+)
- Creating schemas/neutral-model/ before Gate 4 is approved — FORBIDDEN NOW

---

## Prerequisites

- [ ] Gate 4 PASSED — human approval required (after TC-0018 DEC-034 verification)
- [ ] Explicit Gate 5 planning prompt issued by human

---

## Related Files

- `prototypes/by-format/fods/fods_parser.py` — Gate 4 prototype (input to neutral model design)
- `acquisition-packs/fods/parser-requirements.md` — parser requirements (informs neutral model)
- `acquisition-packs/fods/parser-scope.md` — parser scope
- `docs/gates.md` — Gate 5 criteria
- `taskcards/TC-0017-fods-gate4-parser-prototype-execution.md` — Gate 4 execution (predecessor)
- `taskcards/TC-0018-fods-gate4-parser-prototype-verification.md` — Gate 4 DEC-034 (must complete first)
