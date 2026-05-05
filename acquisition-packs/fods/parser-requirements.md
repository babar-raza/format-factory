---
artifact_id: fods-parser-requirements
artifact_type: acquisition-pack
path: acquisition-packs/fods/parser-requirements.md
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
notes: "FODS parser requirements document. Created run028 (2026-05-05) as Gate 4 parser planning package. Derived from parser-requirements-draft.yaml (local-only, .local/spec-cache/fods/1.3/normalized/). Committed version consolidates MUST/SHOULD/MAY requirements with spec citations."
---

# FODS Parser Requirements

**Format:** Flat OpenDocument Spreadsheet (FODS)
**Spec:** ODF 1.3 Part 3 (OpenDocument-v1.3-os-part3-schema.pdf)
**Spec SHA-256:** sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
**Created:** 2026-05-05 (run028)
**Source:** Derived from `.local/spec-cache/fods/1.3/normalized/parser-requirements-draft.yaml` (local-only)
**Gate:** Gate 4 (Parser Prototype)

---

## Purpose

This document records the parser requirements for the FODS format. It serves as the specification contract for the Gate 4 parser prototype (`prototypes/by-format/fods/fods_parser.py`). Each requirement is tagged with a priority and a spec citation.

Requirements are derived from:
1. `parser-requirements-draft.yaml` (local-only, produced run026)
2. ODF 1.3 spec queries via `query_normalized_spec.py` (run026)
3. The 4 Gate 3 sample files in `samples/by-format/fods/`

---

## Requirement Summary

| Req ID | Capability | Priority | Spec Section |
|---|---|---|---|
| PR-001 | Parse root `<office:document>` element | MUST | §3.1.2 |
| PR-002 | Validate FODS mimetype | MUST | §3.1.2 |
| PR-003 | Navigate `office:body > office:spreadsheet` | MUST | §3.7 |
| PR-004 | Enumerate `table:table` elements (sheets) | MUST | §9.4 |
| PR-005 | Read `table:table-row` elements | MUST | §9.4 |
| PR-006 | Read `table:table-cell` and typed values | MUST | §9.4 |
| PR-007 | Handle `table:number-columns-repeated` | MUST | §9.1.5 |
| PR-008 | Read string cell text from `<text:p>` | MUST | §9.1.4 |
| PR-009 | Read `table:formula` attribute | SHOULD | §9.4 |
| PR-010 | Register required XML namespaces | MUST | §3.1.2 |

---

## Detailed Requirements

### PR-001 — Parse root `<office:document>` element

**Priority:** MUST
**Spec citation:** ODF 1.3 §3.1.2 — "The root element of a flat XML document shall be `<office:document>`."
**Retrieval method:** tier1_section (`--section 3.1.2`)

The parser must parse the root element `<office:document>` and extract:
- `office:mimetype` attribute (used in PR-002)
- `office:version` attribute (ODF version)
- All child elements (for navigation in PR-003)

The root element must be present; if absent the file is not a conforming FODS document.

---

### PR-002 — Validate FODS mimetype

**Priority:** MUST
**Spec citation:** ODF 1.3 §3.1.2 — mimetype for flat XML spreadsheet is `application/vnd.oasis.opendocument.spreadsheet-flat-xml`
**Retrieval method:** tier1_element (`--element "office:document"`)

The parser must check the `office:mimetype` attribute equals:
```
application/vnd.oasis.opendocument.spreadsheet-flat-xml
```
If the mimetype is absent or does not match, the parser must return a parse error with the actual mimetype value for diagnostic purposes.

---

### PR-003 — Navigate `office:body > office:spreadsheet`

**Priority:** MUST
**Spec citation:** ODF 1.3 §3.7 — "A spreadsheet document's body is an `<office:spreadsheet>` element."
**Retrieval method:** tier1_section (`--section 3.7`)

The parser must navigate from the root element to the spreadsheet content container:
```
<office:document>
  <office:body>
    <office:spreadsheet>   ← this is the content root
```
If `<office:spreadsheet>` is absent inside `<office:body>`, the document is not a conforming spreadsheet FODS.

---

### PR-004 — Enumerate `table:table` elements (sheets)

**Priority:** MUST
**Spec citation:** ODF 1.3 §9.4 — sheets are represented as `<table:table>` elements inside `<office:spreadsheet>`
**Retrieval method:** tier1_element (`--element "table:table"`)

The parser must enumerate all `<table:table>` elements as sheets. For each sheet it must extract:
- `table:name` attribute (sheet name)
- `table:style-name` attribute (optional; for future style parsing)
- All child `<table:table-row>` elements (for PR-005)

---

### PR-005 — Read `table:table-row` elements

**Priority:** MUST
**Spec citation:** ODF 1.3 §9.4 — rows are `<table:table-row>` elements inside `<table:table>`
**Retrieval method:** tier1_element (`--element "table:table-row"`)

For each row the parser must extract:
- `table:number-rows-repeated` attribute (if present): the row is repeated N times
- All child `<table:table-cell>` and `<table:covered-table-cell>` elements (for PR-006)

Repeated rows must be expanded (or tracked as a repeated span) before yielding cell values.

---

### PR-006 — Read `table:table-cell` and typed values

**Priority:** MUST
**Spec citation:** ODF 1.3 §9.4 — cells are `<table:table-cell>` elements; typed values are represented via `office:value-type`
**Retrieval method:** tier2_keyword (`--keyword "office:value-type"`)

The parser must extract typed cell values. Supported `office:value-type` values:

| Value type | Attribute for value | Notes |
|---|---|---|
| `float` | `office:value` | Numeric (integer, decimal) |
| `string` | (none; text in `<text:p>`) | String cell |
| `boolean` | `office:boolean-value` | "true"/"false" |
| `date` | `office:date-value` | ISO-8601 date |
| `time` | `office:time-value` | ISO-8601 duration |
| `currency` | `office:value` | Numeric with currency-symbol |
| `percentage` | `office:value` | Numeric (fraction) |

If `office:value-type` is absent, the cell is empty (unless it contains a formula in PR-009).

---

### PR-007 — Handle `table:number-columns-repeated`

**Priority:** MUST
**Spec citation:** ODF 1.3 §9.1.5 — cells may carry `table:number-columns-repeated` to indicate repetition
**Retrieval method:** tier2_keyword (`--keyword "number-columns-repeated"`)

Cells with `table:number-columns-repeated="N"` must be treated as N consecutive cells with the same value and type. This is used heavily for empty trailing cells in rows. The parser must expand or represent these correctly — callers must receive correct column counts.

---

### PR-008 — Read string cell text from `<text:p>`

**Priority:** MUST
**Spec citation:** ODF 1.3 §9.1.4 — cell text content is in `<text:p>` child elements
**Retrieval method:** tier1_element (`--element "text:p"`)

For cells with `office:value-type="string"` (and for display text of other cell types), the parser must concatenate the text content of all `<text:p>` child elements. Multiple `<text:p>` elements represent paragraphs; they must be joined with a newline for the Gate 4 prototype (higher-fidelity text handling is a Gate 5+ concern).

---

### PR-009 — Read `table:formula` attribute

**Priority:** SHOULD
**Spec citation:** ODF 1.3 §9.4 — formula cells carry `table:formula` attribute
**Retrieval method:** tier2_keyword (`--keyword "table:formula"`)

Cells with a `table:formula` attribute are formula cells. The parser should:
1. Return the formula string as a raw attribute value (no evaluation).
2. Also return the cached `office:value` and `office:value-type` if present (the cell's last computed value).

Formula evaluation is NOT in scope for Gate 4.

---

### PR-010 — Register required XML namespaces

**Priority:** MUST
**Spec citation:** ODF 1.3 §3.1.2 — FODS documents use multiple XML namespaces
**Retrieval method:** tier1_section (`--section 3.1.2`)

The parser must register (at minimum) the following XML namespace prefixes to parse FODS correctly:

| Prefix | Namespace URI |
|---|---|
| `office` | `urn:oasis:names:tc:opendocument:xmlns:office:1.0` |
| `table` | `urn:oasis:names:tc:opendocument:xmlns:table:1.0` |
| `text` | `urn:oasis:names:tc:opendocument:xmlns:text:1.0` |
| `style` | `urn:oasis:names:tc:opendocument:xmlns:style:1.0` |
| `fo` | `urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0` |
| `oooc` | `http://openoffice.org/2004/calc` |

A conforming ODF 1.3 FODS document declares these namespaces on the root element. The parser must not hard-code namespace prefixes; it must use the declared URI mappings from the document itself.

---

## Out-of-Scope for Gate 4 Prototype

The following capabilities are intentionally excluded from the Gate 4 prototype:

- **Formula evaluation** — formula strings are extracted raw; no computation
- **Style inheritance** — `table:style-name` and paragraph styles are noted but not resolved
- **Conditional formatting** — future gate concern
- **Merged cells** (`table:covered-table-cell`) — detected but not fully expanded
- **Embedded objects / images** — out of scope (Gate 5+ neutral model concern)
- **Macro/script content** — never parsed (security boundary)
- **Annotations / comments** — out of scope for Gate 4
- **Chart/pivot data** — out of scope for Gate 4

---

## Spec Citation Provenance

All requirements above are derived from ODF 1.3 Part 3 (schema spec):

```yaml
spec_citation:
  spec_version: "ODF 1.3"
  source_hash: "sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066"
  retrieval_method: "tier1_section | tier1_element | tier2_keyword"
  local_path: ".local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf"
```

---

## Revision History

| Run | Change |
|---|---|
| run026 | `parser-requirements-draft.yaml` produced (local-only) from spec queries + sample inspection |
| run028 | This document created from draft; requirements formalized with spec citations; committed as Gate 4 planning artifact |
