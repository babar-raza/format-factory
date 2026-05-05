---
artifact_id: fods-parser-scope
artifact_type: acquisition-pack
path: acquisition-packs/fods/parser-scope.md
format_id: fods
product_family: cells
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: true
refresh_policy:
  trigger: spec-version-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS Gate 4 parser scope document. Created run028 (2026-05-05). Defines prototype scope, tier targets, forbidden actions, and handoff contract."
---

# FODS Parser Scope — Gate 4

**Format:** Flat OpenDocument Spreadsheet (FODS)
**Created:** 2026-05-05 (run028)
**Gate:** Gate 4 (Parser Prototype)
**Status:** planning_ready — awaiting explicit Gate 4 execution prompt

---

## Purpose

This document defines the scope of the Gate 4 FODS parser prototype. It supplements `parser-requirements.md` (what the parser must do) with a clear boundary for what is and is not built in Gate 4.

Gate 4 produces a working proof-of-concept prototype. It is NOT product code. It is evidence that the parser requirements are implementable and that the 4 Gate 3 samples can be read correctly.

---

## In Scope for Gate 4

| Item | Description |
|---|---|
| Prototype location | `prototypes/by-format/fods/fods_parser.py` |
| Language | Python 3.11+ |
| Dependencies | stdlib only (`xml.etree.ElementTree`) — no third-party XML libraries |
| Sample targets | All 4 Gate 3 samples: `minimal-spreadsheet.fods`, `multi-sheet-basic.fods`, `typed-values-basic.fods`, `formula-basic.fods` |
| Output format | JSON — normalized representation of sheets, rows, and cells |
| Validation | Parser output for each sample matches expected cell values (manual golden record) |
| Parser notes | `acquisition-packs/fods/parser-notes.md` (Gate 4 deliverable) |
| Requirements committed | `parser-requirements-draft.yaml` → committed as `acquisition-packs/fods/parser-requirements.md` (done run028) |

---

## Functional Scope

The Gate 4 prototype must:

1. Accept a file path to a FODS file.
2. Parse the root `<office:document>` element and validate the mimetype (PR-001, PR-002).
3. Navigate to `<office:spreadsheet>` (PR-003).
4. Enumerate all sheets (`<table:table>`) (PR-004).
5. For each sheet, enumerate all rows (`<table:table-row>`) (PR-005).
6. For each row, enumerate all cells (`<table:table-cell>`) (PR-006).
7. Handle `table:number-columns-repeated` correctly (PR-007).
8. Extract string cell text from `<text:p>` (PR-008).
9. Extract formula attribute raw value (PR-009 — SHOULD, best effort).
10. Register all required XML namespaces (PR-010).

Output schema (JSON):
```json
{
  "format": "fods",
  "spec_version": "ODF 1.3",
  "sheets": [
    {
      "name": "Sheet1",
      "rows": [
        {
          "index": 0,
          "cells": [
            {
              "col_index": 0,
              "value_type": "float",
              "value": 42.0,
              "text": "42",
              "formula": null
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Tier Scope

| Tier | Description | In Gate 4? |
|---|---|---|
| Tier 0 | Detect format (mimetype check) | YES — PR-002 |
| Tier 1 | Read metadata and structure (sheet names, row/cell count) | YES — PR-003, PR-004 |
| Tier 2 | Import core content (cell values, typed values) | YES — PR-006, PR-007, PR-008 |
| Tier 3 | Export (round-trip) | NO — Gate 5+ |
| Tier 4 | Roundtrip fidelity | NO — Gate 5+ |
| Tier 5+ | Commercial fidelity | NO — Gate 9+ |

---

## Out of Scope — FORBIDDEN at Gate 4

| Item | Why forbidden |
|---|---|
| Gate 4 self-approval | Human-only (rule #14) |
| Neutral model schema (`schemas/neutral-model/`) | Gate 5 |
| Product source (`src/python/fods/`, `src/net/fods/`) | Gate 9+ |
| Oracle comparison | Gate 6 |
| Fuzz testing | Gate 7 |
| Security report | Gate 8 |
| Formula evaluation | Out of scope; formula string extraction only |
| Style resolution | Gate 5+ concern |
| Third-party parser libraries (lxml, defusedxml for parsing logic) | stdlib only for prototype |
| Committing `.local/spec-cache/` normalized artifacts | Never committed |

---

## Parser Notes Document

The Gate 4 execution produces `acquisition-packs/fods/parser-notes.md`. This document records:
- Parser design decisions (why stdlib ElementTree, not lxml)
- Known limitations of the prototype relative to the full ODF 1.3 spec
- Edge cases discovered during prototype development
- Security observations (XXE risk — mitigated by `xml.etree.ElementTree` defaults)

`parser-notes.md` is a Gate 4 deliverable. It is NOT this document (`parser-scope.md`).

---

## Handoff Contract

The Gate 4 prototype handoff to human review requires:
1. `prototypes/by-format/fods/fods_parser.py` — reads all 4 samples correctly
2. Parser JSON output for each sample (included in evidence bundle)
3. `acquisition-packs/fods/parser-notes.md` — design decisions and limitations
4. Gate 4 independent verification (DEC-034) before human review
5. Registry `gate_4.status` updated to `prototype_created_pending_independent_verification`

---

## Security Baseline (Gate 4)

The Gate 4 prototype must document:

| Risk | Mitigation |
|---|---|
| XXE (XML External Entity injection) | Python `xml.etree.ElementTree` resolves external entities by default; prototype must NOT use `lxml` without `resolve_entities=False`; stdlib ET is safe for trusted inputs |
| Path traversal | File path input must be validated (canonical path, within project directory) |
| Denial of service (deeply nested XML) | Prototype is for trusted test samples only; not a production hardening concern at Gate 4 |
| Macro content | FODS has no macro execution path in the XML structure parsed; macros are in separate elements not traversed by the prototype |

Full security review is Gate 8. Gate 4 only requires a security baseline note in `parser-notes.md`.

---

## Revision History

| Run | Change |
|---|---|
| run028 | Document created as Gate 4 parser planning artifact |
