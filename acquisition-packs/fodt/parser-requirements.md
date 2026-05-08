---
artifact_id: fodt-parser-requirements
artifact_type: acquisition-pack
path: acquisition-packs/fodt/parser-requirements.md
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
notes: "FODT parser requirements. Created run044 (2026-05-08) after Gate 3 PASSED. Gate 4 parser prototype planning. Derived from ODF 1.3 spec (shared with FODS acquisition) + FODT Gate 3 sample analysis."
---

# FODT Parser Requirements — Gate 4

**Format:** Flat OpenDocument Text (FODT)
**Spec:** ODF 1.3 Part 3 (OpenDocument-v1.3-os-part3-schema.pdf)
**Spec SHA-256:** sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
**Created:** 2026-05-08 (run044)
**Gate:** Gate 4 (Parser Prototype)

---

## Purpose

This document defines the parser requirements for the FODT format Gate 4 prototype.
These requirements derive from:
1. ODF 1.3 spec (cached, normalized — same spec as FODS acquisition)
2. The 4 Gate 3 FODT samples in `samples/by-format/fodt/`
3. The FODS parser requirements (reuse pattern — `acquisition-packs/fods/parser-requirements.md`)

---

## Requirement Summary

| Req ID | Capability | Priority | Spec Section | Sample Coverage |
|---|---|---|---|---|
| FR-001 | Parse XML + verify root element + MIME type | P0 | §2 (document structure) | All 4 |
| FR-002 | Extract `text:p` paragraph text | P0 | §5.1 | minimal, headings |
| FR-003 | Extract `text:h` heading text + `text:outline-level` | P0 | §3.1, §5.3 | headings-and-paragraphs |
| FR-004 | Extract `text:list` bullet + numbered items | P1 | §5.3 | list-basic |
| FR-005 | Extract `table:table` rows + cells within office:text | P1 | §14 | table-basic |
| FR-006 | Compute document word count (text from all paragraphs) | P1 | §5.1 | All 4 |
| FR-007 | Return structured error on malformed XML (ParseError / RecursionError) | P0 | — | — |

---

## Detailed Requirements

### FR-001: Root Element and MIME Type Verification

**Priority:** P0 (parser must not proceed on wrong file type)

The parser must verify:
- Root element is `{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document` (i.e. `office:document`)
- `office:mimetype` attribute equals `"application/vnd.oasis.opendocument.text-flat-xml"`
- `office:version` attribute is present (must be "1.3" for this corpus)

**On failure:** Return `{"errors": ["wrong_root_element" | "wrong_mime_type"]}`, not raise.

**Spec ref:** ODF 1.3 §2 — Document Structure; office:document element definition.

---

### FR-002: Paragraph Extraction (text:p)

**Priority:** P0 (paragraphs are the primary content unit)

The parser must extract all `text:p` elements within `office:body/office:text`, returning:
```python
{
  "element": "paragraph",
  "text": str,          # full text content (itertext() concatenation)
  "style_name": str,    # text:style-name attribute, or "Default" if absent
  "outline_level": None # always None for text:p (use 0 or null)
}
```

**Note:** `text:p` inside `table:table-cell` is also captured when table extraction runs (FR-005).

**Spec ref:** ODF 1.3 §5.1.2 — text:p element.

---

### FR-003: Heading Extraction (text:h)

**Priority:** P0 (headings define document structure)

The parser must extract all `text:h` elements within `office:body/office:text`, returning:
```python
{
  "element": "heading",
  "text": str,
  "style_name": str,
  "outline_level": int   # text:outline-level attribute value (1..10)
}
```

**Spec ref:** ODF 1.3 §3.1 — Headings; §5.3 — text:h element definition.

---

### FR-004: List Extraction (text:list)

**Priority:** P1 (required to validate list-basic.fodt sample)

The parser must extract all `text:list` elements within `office:body/office:text`, returning:
```python
{
  "element": "list",
  "items": [
    {
      "text": str,     # full text of text:list-item > text:p
      "level": int     # nesting depth (1 = top-level)
    }
  ]
}
```

Distinguish bullet vs numbered lists using `text:list-level-style-bullet` vs
`text:list-level-style-number` in the automatic-styles section. Record as `list_style: "bullet" | "numbered" | "unknown"`.

**Spec ref:** ODF 1.3 §5.3.1 — text:list; §5.3.2 — text:list-item.

---

### FR-005: Table Extraction (table:table within office:text)

**Priority:** P1 (required to validate table-basic.fodt sample)

The parser must extract all `table:table` elements within `office:body/office:text`, returning:
```python
{
  "element": "table",
  "name": str,       # table:name attribute
  "rows": [
    ["cell1text", "cell2text", ...]   # list of lists (row-major)
  ]
}
```

Cell text is extracted from `table:table-cell > text:p` (innerText).

**Spec ref:** ODF 1.3 §14 — Tables; table:table, table:table-row, table:table-cell elements.

---

### FR-006: Word Count

**Priority:** P1 (useful structural metric)

The parser must compute and return:
- `word_count: int` — total words across all `text:p` and `text:h` elements (split by whitespace)

This provides a document summary metric without requiring a full text extraction mode.

---

### FR-007: Error Handling

**Priority:** P0 (safety requirement, also required for Gate 7 fuzz testing)

The parser must:
1. Catch `xml.etree.ElementTree.ParseError` from `ET.parse()` and return `{"errors": ["parse_error: " + str(e)]}` without re-raising
2. Catch `RecursionError` from deeply nested XML and return `{"errors": ["recursion_limit_exceeded"]}`
3. Never raise unhandled exceptions to the caller

---

## Out of Scope at Gate 4

| Feature | Earliest Gate |
|---|---|
| Style inheritance resolution | Gate 5 (neutral model) |
| Embedded images or binary content | Gate 5+ |
| Comments / annotations | Gate 5+ |
| Change-tracking (tracked changes) | Gate 5+ |
| Metadata extraction (dc:title, dc:creator) | Gate 4 optional (P2) |
| Character-level formatting (text:span) | Gate 4 optional (P2) |
