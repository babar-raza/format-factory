---
artifact_id: TC-0033-fods-gate7-malformed-fuzz-testing
artifact_type: taskcard
path: taskcards/TC-0033-fods-gate7-malformed-fuzz-testing.md
format_id: fods
product_family: cells
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
notes: "FODS Gate 7 malformed/fuzz testing taskcard. Created run044 (2026-05-08) after Gate 6 PASSED. Planning only — execution requires explicit Gate 7 execution prompt."
---

# TC-0033: FODS Gate 7 — Malformed Input and Fuzz Testing

**Taskcard ID:** TC-0033
**Phase:** 3 (Gate 7 — malformed/fuzz testing)
**Gate:** Gate 7
**Status:** not_started — awaiting explicit Gate 7 execution prompt
**Created:** 2026-05-08 (run044)
**Created by:** claude-sonnet-4-6 (run044)
**Prerequisite:** Gate 6 PASSED ✓ (Babar Raza, 2026-05-08, run044)
**Blocking:** Gate 7 human approval

---

## STOP — Authorization Required

**This taskcard must not be executed until a human issues an explicit Gate 7 execution prompt.**

Per AGENTS.md: Gate 7 malformed/fuzz testing requires an explicit human prompt. Planning
documents (this taskcard + `gate7-malformed-fuzz-plan.md` + `gate7-risk-scope.md`) are
created in run044, but execution is blocked until the next session with explicit authorization.

---

## Objective

Execute malformed input and mutation-based fuzz testing against the FODS parser prototype.
Verify the parser handles invalid, truncated, and adversarial inputs safely — without crashes,
panics, or catastrophic resource consumption. Produce a Gate 7 evidence report.

---

## Scope

### In scope

1. **Malformed XML corpus** — hand-crafted invalid FODS files:
   - Truncated files (partial XML)
   - Well-formed XML but invalid ODF structure (wrong root element, missing office:text)
   - Invalid namespace declarations
   - Encoding corruption (BOM, null bytes)
   - Deeply nested structures (stack overflow test)
   - Large attribute values / large text content
   - Missing required elements (office:body absent)
   - Invalid value types (office:value-type="unknown")
   - Circular references in formula text

2. **Mutation-based testing** — mutate the 4 Gate 3 samples:
   - Bit-flip mutations on XML tag names
   - Delete mandatory elements
   - Inject unexpected namespaces
   - Truncate at byte boundaries

3. **Parser safety assertions** — for each malformed input:
   - Parser does not crash (no unhandled exception)
   - Parser returns an error result (not silent corruption)
   - Memory consumption does not grow without bound
   - Time to failure is bounded (no infinite loops)

4. **Gate 7 evidence report** — `acquisition-packs/fods/gate7-malformed-fuzz-report.md`:
   - Total inputs tested
   - Crash count (must be 0)
   - Silent corruption count (must be 0)
   - Error result count
   - Any parser bugs found and fixed

### Out of scope — FORBIDDEN

| Item | Reason | Gate |
|---|---|---|
| Product source code | Gate 10+ | `src/python/fods/`, `src/net/fods/` |
| Gate 7 self-approval | Human-only | — |
| Security audit | Gate 8 | — |
| Fuzz corpus delivery | Gate 7 creates test inputs, not committed fuzz corpus | — |
| CI workflows | Gate 10+ | — |
| New neutral model fields | Requires separate TC | — |

---

## Related Files

- `acquisition-packs/fods/gate7-malformed-fuzz-plan.md` — detailed fuzz plan (run044)
- `acquisition-packs/fods/gate7-risk-scope.md` — risk scope analysis (run044)
- `prototypes/by-format/fods/fods_parser.py` — parser to be tested
- `samples/by-format/fods/` — Gate 3 samples (mutation base)

---

## DEC-034 Requirement

Per DEC-034 and AGENTS.md Section V: after Gate 7 execution, a separate independent
verification sprint (TC-0034-gate7-dec034) must be run before Gate 7 is submitted for
human approval.

TC-0034 (Gate 7 DEC-034 verification) will be created when Gate 7 execution planning is
confirmed. It will require a separate execution session from the Gate 7 execution session.

---

## Evidence Contract

Gate 7 evidence bundle must include:
- `acquisition-packs/fods/gate7-malformed-fuzz-report.md`
- `tests/fixtures/fods/malformed/` directory (malformed test inputs)
- Parser test output showing PASS/FAIL per malformed input
- Self-challenge answers

Gate 7 execution is blocked until this TC-0033 planning is reviewed and an explicit
execution prompt is issued.
