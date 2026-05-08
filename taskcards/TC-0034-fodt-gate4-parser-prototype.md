---
artifact_id: TC-0034-fodt-gate4-parser-prototype
artifact_type: taskcard
path: taskcards/TC-0034-fodt-gate4-parser-prototype.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 4 parser prototype taskcard. Created run044 (2026-05-08) after Gate 3 PASSED. Execution requires explicit Gate 4 execution prompt."
---

# TC-0034: FODT Gate 4 — Parser Prototype

**Taskcard ID:** TC-0034
**Phase:** 3 (Gate 4 — parser prototype)
**Gate:** Gate 4
**Status:** completed — FODT_PROTOTYPE_VALIDATION: PASS 4/4 (run045, 2026-05-08). Gate 4 APPROVED Babar Raza.
**Created:** 2026-05-08 (run044)
**Created by:** claude-sonnet-4-6 (run044)
**Prerequisite:** Gate 3 PASSED ✓ (Babar Raza, 2026-05-08, run044)
**Blocking:** Gate 4 human approval
**DEC-034:** TC-0035 required (separate session after TC-0034 execution)

---

## STOP — Authorization Required

**This taskcard must not be executed until a human issues an explicit Gate 4 execution prompt.**

Per AGENTS.md: Gate 4 parser prototype creation requires an explicit human authorization
prompt. TC-0034 planning documents are created run044, but execution is blocked.

After TC-0034 execution, TC-0035 DEC-034 independent verification must run in a separate
session before Gate 4 is submitted for human approval.

---

## Objective

Create a minimal viable FODT parser prototype at `prototypes/by-format/fodt/fodt_parser.py`.
Validate it against all 4 Gate 3 FODT samples. Produce prototype-notes.md documenting
coverage, assumptions, and limitations.

---

## Deliverables

| File | Description |
|---|---|
| `prototypes/by-format/fodt/fodt_parser.py` | FODT parser prototype (ElementTree, stdlib only) |
| `prototypes/by-format/fodt/validate_against_samples.py` | Validation script against 4 Gate 3 samples |
| `prototypes/by-format/fodt/README.md` | Prototype description |
| `prototypes/by-format/fodt/prototype-notes.md` | Coverage, assumptions, Gate 4 pass evidence |

**Validation target:** 4/4 PASS against Gate 3 FODT samples.

---

## Parser Requirements Summary (from gate4-parser-prototype-plan.md)

| Req ID | Capability | Priority |
|---|---|---|
| FR-001 | Parse XML, verify root element and MIME type | P0 |
| FR-002 | Extract `text:p` paragraph text | P0 |
| FR-003 | Extract `text:h` heading text and outline-level | P0 |
| FR-004 | Extract `text:list` bullet and numbered lists | P1 |
| FR-005 | Extract `table:table` cells within text context | P1 |
| FR-006 | Extract document word count | P1 |
| FR-007 | Return structured error on malformed XML | P0 |

---

## Scope

### In scope

1. `prototypes/by-format/fodt/fodt_parser.py` — ElementTree-based prototype
2. `prototypes/by-format/fodt/validate_against_samples.py` — validates against 4 Gate 3 samples
3. `prototypes/by-format/fodt/prototype-notes.md` — coverage evidence
4. `acquisition-packs/fodt/parser-notes.md` — update status to prototype_created

### Out of scope — FORBIDDEN

| Item | Reason | Gate |
|---|---|---|
| Product source code | Gate 10+ | src/python/fodt/, src/net/fodt/ |
| Gate 4 self-approval | Human-only | — |
| Neutral model (Gate 5) | Separate TC after Gate 4 | — |
| Oracle comparison (Gate 6) | Separate gate after Gate 5 | — |
| Security audit | Gate 8 | — |

---

## Related Files

- `acquisition-packs/fodt/gate4-parser-prototype-plan.md` — detailed plan (run044)
- `acquisition-packs/fodt/parser-requirements.md` — parser requirements (run044)
- `acquisition-packs/fodt/parser-scope.md` — scope definition (run044)
- `acquisition-packs/fodt/parser-test-plan.md` — test plan (run044)
- `acquisition-packs/fodt/parser-notes.md` — planning skeleton (run041)
- `prototypes/by-format/fods/fods_parser.py` — FODS prototype (reuse pattern)
