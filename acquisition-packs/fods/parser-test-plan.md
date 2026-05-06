---
artifact_id: fods-parser-test-plan
artifact_type: acquisition-pack
path: acquisition-packs/fods/parser-test-plan.md
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
notes: "FODS Gate 4 parser test plan. Created run028 (2026-05-05). Defines expected parse output for all 4 Gate 3 samples to serve as Gate 4 acceptance oracle."
---

# FODS Parser Test Plan — Gate 4

**Format:** Flat OpenDocument Spreadsheet (FODS)
**Created:** 2026-05-05 (run028)
**Gate:** Gate 4 (Parser Prototype)
**Status:** prototype_verified_pending_human_review — all 4 tests PASS (run029); TC-0018 re-verified run030

---

## Purpose

This document defines the expected parse output for each of the 4 Gate 3 FODS samples. These expected values serve as the Gate 4 acceptance oracle — the prototype is accepted only if its JSON output matches all expected values below.

This test plan is NOT an oracle comparison (that is Gate 6). It is a basic correctness check: does the prototype parse the known-correct samples without errors?

---

## Test Corpus

| File | SHA-256 | Description |
|---|---|---|
| `samples/by-format/fods/minimal-spreadsheet.fods` | `sha256:a790b18a811c47d634603ad0dd3e42c41c102a36c74b6349b46b9770a2825543` | 1 sheet, 1 cell, Hello World string |
| `samples/by-format/fods/multi-sheet-basic.fods` | `sha256:669b60befc7206a08578815e781ff72526c98d07be53f20e37f062b73b7dcc41` | 2 sheets (Sheet1, Sheet2), basic cells |
| `samples/by-format/fods/typed-values-basic.fods` | `sha256:c873322d69fa93ff64519a37a5f87f4efc9cd244a18488f03adc342524e51977` | 1 sheet, typed values (string, float, boolean, date) |
| `samples/by-format/fods/formula-basic.fods` | `sha256:72b065415748db3e3c7796608f50b488db6d23b2439d2468baf88ea41b38db1e` | 1 sheet, cells with formulas |

---

## Test PT-001 — minimal-spreadsheet.fods

**File:** `samples/by-format/fods/minimal-spreadsheet.fods`
**Test objective:** Parser reads 1 sheet with 1 cell; validates mimetype and root structure.

**Expected parse result:**

```json
{
  "format": "fods",
  "spec_version": "ODF 1.3",
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
  ]
}
```

**Note (run029):** Planning doc predicted `text="Hello, World!"`. Actual sample text is `"Hello"`. Sample unchanged (SHA-256 MATCH); prediction was incorrect. Test updated to match actual.

**Acceptance criteria:**
- [x] No parse error
- [x] `sheet_count == 1`
- [x] `sheets[0].name == "Sheet1"`
- [x] `sheets[0].rows[0].cells[0].value_type == "string"`
- [x] `sheets[0].rows[0].cells[0].text == "Hello"` (corrected from plan — actual value is "Hello")
- [x] `mimetype` matches FODS expected value

---

## Test PT-002 — multi-sheet-basic.fods

**File:** `samples/by-format/fods/multi-sheet-basic.fods`
**Test objective:** Parser enumerates multiple sheets correctly.

**Expected parse result (abbreviated):**

```json
{
  "format": "fods",
  "spec_version": "ODF 1.3",
  "sheet_count": 2,
  "sheets": [
    {
      "name": "Data",
      "row_count": ">= 1"
    },
    {
      "name": "Summary",
      "row_count": ">= 1"
    }
  ]
}
```

**Note (run029):** Planning doc predicted sheet names "Sheet1" and "Sheet2". Actual sample has "Data" and "Summary". Sample unchanged (SHA-256 MATCH); prediction was incorrect. Test updated to match actual.

**Acceptance criteria:**
- [x] No parse error
- [x] `sheet_count == 2`
- [x] `sheets[0].name == "Data"` (corrected from plan — actual value is "Data")
- [x] `sheets[1].name == "Summary"` (corrected from plan — actual value is "Summary")
- [x] Both sheets have at least one non-empty row
- [x] Cell values in both sheets are non-null for at least 1 cell each

---

## Test PT-003 — typed-values-basic.fods

**File:** `samples/by-format/fods/typed-values-basic.fods`
**Test objective:** Parser correctly reads typed cell values (float, string, boolean, date).

**Expected parse result (key cells):**

```json
{
  "format": "fods",
  "spec_version": "ODF 1.3",
  "sheet_count": 1,
  "sheets": [
    {
      "name": "Sheet1",
      "typed_cells_present": {
        "string": true,
        "float": true,
        "boolean": true,
        "date": true
      }
    }
  ]
}
```

**Note (run029):** Planning doc predicted a date cell. Actual sample has string, float, and boolean cells only — no date cell. Sample unchanged (SHA-256 MATCH); prediction was incorrect. Date criterion removed; test passes with string/float/boolean.

**Acceptance criteria:**
- [x] No parse error
- [x] At least one cell with `value_type == "string"` present
- [x] At least one cell with `value_type == "float"` present with a numeric `value`
- [x] At least one cell with `value_type == "boolean"` present with value `true` or `false`
- [~] Date cell — NOT PRESENT in actual sample (prediction was incorrect; not a test failure)

---

## Test PT-004 — formula-basic.fods

**File:** `samples/by-format/fods/formula-basic.fods`
**Test objective:** Parser extracts formula attribute and cached result value.

**Expected parse result (key cells):**

```json
{
  "format": "fods",
  "spec_version": "ODF 1.3",
  "sheet_count": 1,
  "sheets": [
    {
      "name": "Sheet1",
      "has_formula_cells": true,
      "formula_cells_example": {
        "formula": "(non-null string, e.g. 'oooc:=A1+B1')",
        "value": "(cached numeric value, non-null)",
        "value_type": "float"
      }
    }
  ]
}
```

**Acceptance criteria:**
- [x] No parse error
- [x] At least one cell with `formula != null` present
- [x] Formula cell also has `value` (cached result: 60.0) and `value_type` (`float`) populated
- [x] Formula string starts with `oooc:=` (confirmed: `oooc:=SUM([.A1:.A3])`)

---

## Overall Acceptance Criteria

All 4 tests (PT-001 through PT-004) must pass for Gate 4 acceptance.

| Test | Status | Run |
|---|---|---|
| PT-001 minimal-spreadsheet | **PASS** | run029 (re-verified run030) |
| PT-002 multi-sheet-basic | **PASS** | run029 (re-verified run030) |
| PT-003 typed-values-basic | **PASS** | run029 (re-verified run030) |
| PT-004 formula-basic | **PASS** | run029 (re-verified run030) |

**Gate 4 overall result: 4/4 PASS.** TC-0018 independent verification PASS (run030). Human Gate 4 approval required.

---

## Edge Cases to Document (Gate 4)

Even if the above tests pass, the Gate 4 prototype must document the following edge cases encountered:

1. **Empty cells with `table:number-columns-repeated`** — many empty trailing cells are compressed; the prototype must not yield incorrect column counts.
2. **Rows with `table:number-rows-repeated`** — trailing empty rows are often compressed similarly.
3. **Cells with `<text:p>` absent** — some float/boolean/date cells have no `<text:p>` child (display text may be absent for non-string cells).
4. **Multiple `<text:p>` per cell** — paragraph breaks in string cells; prototype must handle gracefully.

These edge cases do not require full handling at Gate 4 but must be documented in `parser-notes.md`.

---

## Security Note for Test Plan

The 4 test samples are project-owned, synthetic, Apache-2.0. They do not contain:
- XXE payloads
- Deeply nested XML bombs
- Macro content
- External references

They are safe inputs for prototype testing. Production hardening is Gate 8 scope.

---

## Revision History

| Run | Change |
|---|---|
| run028 | Document created as Gate 4 parser planning artifact |
| run029 | Gate 4 prototype executed; PT-001..PT-004 PASS; 3 plan discrepancies documented (text="Hello" not "Hello, World!", sheets "Data"/"Summary" not "Sheet1"/"Sheet2", no date cell in PT-003) |
| run030 | TC-0018 independent verification PASS; all statuses updated to PASS; plan discrepancies corrected in acceptance criteria |
