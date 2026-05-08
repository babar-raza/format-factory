---
artifact_id: fodt-parser-test-plan
artifact_type: acquisition-pack
path: acquisition-packs/fodt/parser-test-plan.md
format_id: fodt
product_family: words
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: true
refresh_policy:
  trigger: spec-version-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 4 parser test plan. Created run044 (2026-05-08). Defines expected parse output for all 4 Gate 3 FODT samples to serve as Gate 4 acceptance tests."
---

# FODT Parser Test Plan — Gate 4

**Format:** Flat OpenDocument Text (FODT)
**Created:** 2026-05-08 (run044)
**Gate:** Gate 4 (Parser Prototype)

---

## Overview

This test plan defines the expected parse output for each of the 4 Gate 3 FODT samples.
`validate_against_samples.py` must verify all assertions before Gate 4 is considered passing.

---

## Test Cases

### PT-001: minimal-document.fodt

**File:** `samples/by-format/fodt/minimal-document.fodt`
**Coverage:** FR-001, FR-002

**Expected output assertions:**
- `result["mime_type"]` == `"application/vnd.oasis.opendocument.text-flat-xml"`
- `result["version"]` == `"1.3"`
- `len(result["paragraphs"])` >= 1
- `result["paragraphs"][0]["element"]` == `"paragraph"`
- `result["paragraphs"][0]["text"]` is non-empty string
- `result["errors"]` == `[]`

---

### PT-002: headings-and-paragraphs.fodt

**File:** `samples/by-format/fodt/headings-and-paragraphs.fodt`
**Coverage:** FR-001, FR-002, FR-003

**Expected output assertions:**
- `result["mime_type"]` == `"application/vnd.oasis.opendocument.text-flat-xml"`
- `result["errors"]` == `[]`
- At least 1 element with `"element": "heading"` and `"outline_level": 1`
- At least 1 element with `"element": "heading"` and `"outline_level": 2`
- At least 1 element with `"element": "paragraph"`
- All heading `"text"` fields are non-empty strings

---

### PT-003: list-basic.fodt

**File:** `samples/by-format/fodt/list-basic.fodt`
**Coverage:** FR-001, FR-004

**Expected output assertions:**
- `result["errors"]` == `[]`
- `len(result["lists"])` >= 2 (at least 1 bullet list + 1 numbered list)
- At least one list with `"list_style": "bullet"`
- At least one list with `"list_style": "numbered"`
- Each list has `"items"` list with at least 1 item
- Each item has non-empty `"text"` and `"level"` >= 1

---

### PT-004: table-basic.fodt

**File:** `samples/by-format/fodt/table-basic.fodt`
**Coverage:** FR-001, FR-005

**Expected output assertions:**
- `result["errors"]` == `[]`
- `len(result["tables"])` >= 1
- `result["tables"][0]["rows"]` has at least 2 rows (2×3 table in sample)
- Each row has at least 1 cell
- Cell values are strings (may be empty for empty cells)

---

## Test Runner Expected Output

```
PT-001: minimal-document.fodt — PASS
PT-002: headings-and-paragraphs.fodt — PASS
PT-003: list-basic.fodt — PASS
PT-004: table-basic.fodt — PASS

Results: 4/4 PASS
FODT_PROTOTYPE_VALIDATION: PASS
```

---

## Error Test Cases (for Gate 4 error handling)

These are not Gate 3 sample tests — they test FR-007 (error handling):

| Input | Expected result |
|---|---|
| Empty string path (file not found) | `{"errors": ["file_not_found: ..."]}` or raises IOError (acceptable at Gate 4) |
| String with `<invalid xml` | `{"errors": ["parse_error: ..."]}` — no crash |
| Empty file (0 bytes) | `{"errors": ["parse_error: ..."]}` or `{"errors": ["empty_file"]}` |

These error tests are optional at Gate 4 (Gate 7 covers malformed input comprehensively).
