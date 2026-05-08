---
artifact_id: fods-gate7-malformed-fuzz-plan
artifact_type: gate-planning
path: acquisition-packs/fods/gate7-malformed-fuzz-plan.md
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
notes: "FODS Gate 7 malformed/fuzz testing plan. Created run044 (2026-05-08) after Gate 6 PASSED. Planning only — execution requires explicit Gate 7 execution prompt."
---

# FODS Gate 7 — Malformed Input and Fuzz Testing Plan

**Format:** FODS — Flat OpenDocument Spreadsheet
**Gate:** 7 — Malformed/Fuzz Testing
**Status:** planning_only — Gate 6 PASSED; awaiting explicit Gate 7 execution prompt
**Created:** run044 (2026-05-08)
**Prerequisite:** Gate 6 PASSED (Babar Raza, 2026-05-08, run044)

---

## Gate 7 Objectives

Gate 7 verifies that the FODS parser prototype handles malformed and adversarial input safely.
The parser must:
1. Never crash on malformed input (no unhandled exceptions)
2. Always return a structured error result (not silent corruption)
3. Not consume unbounded memory or CPU on pathological input
4. Handle all boundary conditions defined in the ODF 1.3 spec

---

## Test Input Categories

### Category A: XML-Level Malformations (6 inputs)

| Input | Description | Expected parser behavior |
|---|---|---|
| `truncated-mid-tag.fods` | File cut off mid-element tag | ParseError returned, no crash |
| `truncated-mid-attribute.fods` | File cut off mid-attribute value | ParseError returned |
| `no-root-element.fods` | Empty file (0 bytes) | ParseError returned |
| `invalid-xml-chars.fods` | Null bytes embedded in XML | ParseError or sanitized result |
| `deeply-nested.fods` | 1000-deep nested elements | No stack overflow, bounded time |
| `large-attribute.fods` | Single attribute with 1MB value | Bounded memory, no crash |

### Category B: ODF Structure Malformations (6 inputs)

| Input | Description | Expected parser behavior |
|---|---|---|
| `wrong-root-element.fods` | Root is `<spreadsheet>` not `<office:document>` | ParseError: wrong root |
| `missing-office-body.fods` | No `<office:body>` element | ParseError or empty workbook |
| `wrong-mimetype.fods` | `office:mimetype="text/plain"` | Handled: wrong MIME returned or warning |
| `missing-namespace.fods` | `office:` prefix without declaration | ParseError returned |
| `invalid-value-type.fods` | `office:value-type="quaternion"` | Warning emitted, cell value null |
| `missing-table-name.fods` | `table:table` without `table:name` | Handled: default name or warning |

### Category C: Mutation-Based Tests (4 inputs)

One mutation per Gate 3 sample:

| Input | Base sample | Mutation |
|---|---|---|
| `minimal-spreadsheet-mut1.fods` | minimal-spreadsheet.fods | Delete `office:body` element |
| `multi-sheet-mut1.fods` | multi-sheet-basic.fods | Rename `table:table` to `table:worksheet` |
| `typed-values-mut1.fods` | typed-values-basic.fods | Set `office:value-type` to empty string |
| `formula-mut1.fods` | formula-basic.fods | Corrupt `table:formula` to `table:formula="=BADFN("` |

### Category D: Resource Exhaustion Tests (2 inputs)

| Input | Description | Expected parser behavior |
|---|---|---|
| `many-sheets.fods` | 1000 `table:table` elements, each with 1 cell | Parsed successfully or warned; bounded memory |
| `wide-row.fods` | 1 sheet, 1 row with 10,000 cells | Parsed or warned; bounded memory |

---

## Total Test Inputs: 18

---

## Success Criteria

Gate 7 PASSES when:
1. **Crash count = 0** — no unhandled exceptions on any of the 18 inputs
2. **Silent corruption count = 0** — every error input produces an error result or warning
3. **Memory bounded** — no input causes memory to grow beyond 100MB during parsing
4. **Time bounded** — no input takes more than 30 seconds to parse
5. **Gate 7 evidence report** exists at `acquisition-packs/fods/gate7-malformed-fuzz-report.md`
6. **Human has reviewed** and approved the report

---

## Parser Under Test

- `prototypes/by-format/fods/fods_parser.py` (Gate 4 prototype; currently validates 4/4 Gate 3 samples)
- No product source modifications permitted (Gate 10+ authorization required)
- Prototype-level fixes to prevent crashes are authorized (bug fixes, not feature additions)

---

## Test Fixture Location

Malformed test inputs will be created at:
- `tests/fixtures/fods/malformed/` — 18 malformed FODS files (Apache-2.0, project-owned synthetic)

These files will be committed. They are test fixtures, not samples (not in `samples/by-format/fods/`).

---

## Evidence Requirements

Gate 7 evidence bundle must include:
- `acquisition-packs/fods/gate7-malformed-fuzz-report.md` (summary + per-input results)
- `tests/fixtures/fods/malformed/*.fods` (18 test inputs)
- Test runner output (`GATE7_FUZZ_TEST: PASS N/18 CRASH 0/18 CORRUPT 0/18`)

---

## DEC-034 Requirement

After Gate 7 execution, a separate independent verification session must run before
Gate 7 is submitted for human approval. The verification TC will be created when
Gate 7 execution planning is confirmed.

---

## Execution Gate

**Gate 7 execution is blocked until a human issues an explicit Gate 7 execution prompt.**

The execution prompt must state:
- TC-0033 authorized for Gate 7 malformed/fuzz execution
- Session will be separate from the verification session (DEC-034)
- No product source creation
- No Gate 7 self-approval
