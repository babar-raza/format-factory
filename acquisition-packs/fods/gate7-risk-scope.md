---
artifact_id: fods-gate7-risk-scope
artifact_type: gate-planning
path: acquisition-packs/fods/gate7-risk-scope.md
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
notes: "FODS Gate 7 risk and scope analysis. Created run044 (2026-05-08) after Gate 6 PASSED."
---

# FODS Gate 7 — Risk and Scope Analysis

**Format:** FODS — Flat OpenDocument Spreadsheet
**Gate:** 7 — Malformed/Fuzz Testing
**Status:** planning_only
**Created:** run044 (2026-05-08)

---

## Scope Boundaries

### In Scope

| Item | Gate 7 Role |
|---|---|
| Malformed XML inputs (18 test cases) | Test parser safety |
| Parser error handling behavior | Verify crash-free operation |
| Prototype-level crash fixes | Authorized if crashes found |
| Test fixtures at tests/fixtures/fods/malformed/ | Created and committed |
| Gate 7 evidence report | Required deliverable |

### Out of Scope — FORBIDDEN at Gate 7

| Item | Earliest Gate |
|---|---|
| Product source code (src/python/fods/, src/net/fods/) | Gate 10 |
| Security audit (CVEs, formal threat model) | Gate 8 |
| Compliance testing (ODF validator against official test suite) | Gate 8+ |
| Performance benchmarks | Gate 9+ |
| Fuzz corpus with real-world malware samples | Never (policy blocks) |
| Gate 7 self-approval | Human-only |

---

## Risk Register (Gate 7)

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-G7-1 | Parser crashes on malformed XML | Medium | High | ElementTree raises xml.etree.ElementTree.ParseError — catch at parse entry point |
| R-G7-2 | Parser silently returns wrong data on malformed input | Medium | High | Assert error result on known-bad inputs; fail test if no error returned |
| R-G7-3 | Stack overflow on deeply nested XML | Low | High | Python recursion limit (1000) may trigger; wrap in try/except RecursionError |
| R-G7-4 | Memory exhaustion on large inputs | Low | Medium | Set resource limits before test; assert parser terminates within 100MB |
| R-G7-5 | Gate 7 discovers a fundamental parser bug requiring neutral model changes | Low | High | Neutral model changes require a separate TC; Gate 7 only fixes crash/error bugs |
| R-G7-6 | Gate 7 execution and verification in same session (DEC-034 violation) | Low | High | Execution prompt must specify separate sessions; verification TC created in separate run |

---

## Parser Error Handling Model

The FODS parser prototype (`prototypes/by-format/fods/fods_parser.py`) currently:
- Uses `xml.etree.ElementTree` (stdlib)
- `ElementTree.parse()` raises `ParseError` on malformed XML
- The top-level `parse_fods()` function does not currently catch exceptions at the entry level

**Gate 7 requirement**: The prototype must wrap its top-level parse call in a try/except block
that catches `ParseError` (malformed XML) and `RecursionError` (deep nesting) and returns
a structured error result rather than propagating the exception. This is a safety fix, not
a feature addition, and is authorized for the prototype at Gate 7.

---

## What Gate 7 Does NOT Cover

**Security audit (Gate 8)** covers:
- Arbitrary code execution via XML entity injection (XXE)
- Denial-of-service via crafted inputs (billion laughs, quadratic blowup)
- Path traversal via malformed file references

**Gate 7 covers only**: crash-free error handling for common malformed inputs.
Gate 7 explicitly does NOT require the parser to be DoS-hardened (that is Gate 8).

---

## Classification of Gate 7 Test Fixtures

All 18 malformed test fixtures:
- `visibility: internal`
- `license: Apache-2.0`
- `creator: format-factory project`
- `provenance_status: confirmed`
- Purpose: test fixture (not production sample)
- Location: `tests/fixtures/fods/malformed/` (NOT `samples/by-format/fods/`)
