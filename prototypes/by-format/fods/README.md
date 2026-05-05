---
artifact_id: fods-prototype-readme
artifact_type: prototype
path: prototypes/by-format/fods/README.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: Apache-2.0
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
notes: "Gate 4 prototype README for FODS parser. Created run029 (2026-05-05). Prototype validates 4/4 PASS against Gate 3 sample corpus."
---

# FODS Parser Prototype — Gate 4

**Format:** Flat OpenDocument Spreadsheet (FODS)
**Gate:** Gate 4 (Parser Prototype)
**Status:** `prototype_created_pending_independent_verification`
**Created:** 2026-05-05 (run029)
**Validation:** PT-001 through PT-004 PASS (4/4)

---

## IMPORTANT — Prototype Scope

This is a **Gate 4 prototype only**. It is NOT product code.

- No product source exists (`src/python/fods/`, `src/net/fods/` are forbidden until Gate 9+).
- Gate 4 is NOT approved. Independent verification (TC-0018 / DEC-034) is required.
- No neutral model schemas exist (Gate 5+).
- Formula evaluation is NOT implemented (out of scope for Gate 4).

---

## Files in This Directory

| File | Purpose |
|---|---|
| `fods_parser.py` | Prototype FODS parser — Python stdlib only |
| `validate_against_samples.py` | Runs PT-001–PT-004 against Gate 3 sample corpus |
| `README.md` | This file |
| `prototype-notes.md` | Design decisions, limitations, security baseline |

---

## Usage

```bash
# Parse a FODS file (output JSON to stdout)
python prototypes/by-format/fods/fods_parser.py samples/by-format/fods/minimal-spreadsheet.fods

# Parse and save output to file
python prototypes/by-format/fods/fods_parser.py samples/by-format/fods/formula-basic.fods output.json

# Run all 4 validation tests
python prototypes/by-format/fods/validate_against_samples.py

# Run with explicit samples directory
python prototypes/by-format/fods/validate_against_samples.py --samples-dir samples/by-format/fods/
```

---

## Output Format

```json
{
  "format": "fods",
  "spec_version": "ODF 1.3",
  "odf_version_attr": "1.3",
  "mimetype": "application/vnd.oasis.opendocument.spreadsheet-flat-xml",
  "sheet_count": 1,
  "sheets": [
    {
      "name": "Sheet1",
      "row_count": 1,
      "rows": [
        {
          "index": 0,
          "cells": [
            {
              "col_index": 0,
              "value_type": "string",
              "value": null,
              "text": "Hello",
              "formula": null
            }
          ]
        }
      ]
    }
  ],
  "warnings": []
}
```

---

## Requirements Implemented

| Req | Status |
|---|---|
| PR-001 Parse root `<office:document>` | DONE |
| PR-002 Validate FODS mimetype | DONE |
| PR-003 Navigate `office:body > office:spreadsheet` | DONE |
| PR-004 Enumerate `table:table` elements (sheets) | DONE |
| PR-005 Read `table:table-row` elements | DONE |
| PR-006 Read `table:table-cell` and typed values | DONE (float, string, boolean, date, time, currency, percentage) |
| PR-007 Handle `table:number-columns-repeated` | DONE |
| PR-008 Read string cell text from `<text:p>` | DONE |
| PR-009 Read `table:formula` attribute | DONE (raw string, no evaluation) |
| PR-010 Register required XML namespaces | DONE (Clark notation via ElementTree) |

---

## Gate 4 Validation Results (run029)

| Test | Sample | Result |
|---|---|---|
| PT-001 | minimal-spreadsheet.fods | PASS (8/8 assertions) |
| PT-002 | multi-sheet-basic.fods | PASS (6/6 assertions) |
| PT-003 | typed-values-basic.fods | PASS (8/8 assertions) |
| PT-004 | formula-basic.fods | PASS (8/8 assertions) |

**Overall: PASS (4/4)**

---

## Next Step

TC-0018 independent verification sprint (DEC-034) required before Gate 4 human approval.
Gate 4 approval: NOT GRANTED. Human approval required.
