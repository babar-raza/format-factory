---
artifact_id: fodt-prototype-notes
artifact_type: prototype
path: prototypes/by-format/fodt/prototype-notes.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: Apache-2.0
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
notes: "FODT Gate 4 prototype notes. Coverage evidence, assumptions, limitations. run045 (2026-05-08). Validation 4/4 PASS."
---

# FODT Parser Prototype — Notes and Coverage Evidence

**Gate:** 4 (Parser Prototype)
**Run:** run045 (2026-05-08)
**Validation result:** 4/4 PASS (PT-001, PT-002, PT-003, PT-004)
**Approved by:** Babar Raza (2026-05-08, run045 execution prompt)

---

## Gate 4 Pass Evidence

All four test cases from `parser-test-plan.md` passed:

| Test | File | Requirements | Result |
|---|---|---|---|
| PT-001 | minimal-document.fodt | FR-001, FR-002 | PASS |
| PT-002 | headings-and-paragraphs.fodt | FR-001, FR-002, FR-003 | PASS |
| PT-003 | list-basic.fodt | FR-001, FR-004 | PASS |
| PT-004 | table-basic.fodt | FR-001, FR-005 | PASS |

```
Results: 4/4 PASS
FODT_PROTOTYPE_VALIDATION: PASS
```

---

## Requirement Coverage

| Req ID | Capability | Coverage | Notes |
|---|---|---|---|
| FR-001 | Root + MIME type verification | FULL | office:document + mimetype check |
| FR-002 | text:p paragraph extraction | FULL | itertext(), style_name, element type |
| FR-003 | text:h heading extraction | FULL | outline-level, text, style_name |
| FR-004 | text:list extraction + list_style | FULL | bullet/numbered via automatic-styles lookup |
| FR-005 | table:table extraction (rows + cells) | FULL | row-major cell text, table:name |
| FR-006 | word_count | FULL | paragraph + heading text split |
| FR-007 | Error handling (no unhandled exceptions) | FULL | ParseError, OSError, size guard |

---

## Architecture

### FODS Reuse (~40%)

The following patterns were reused directly from `prototypes/by-format/fods/fods_parser.py`:

1. **Namespace constants** — Clark notation `{uri}local` for all element lookups
2. **MAX_FILE_BYTES guard** — 100 MB limit on file size before parsing
3. **Error return model** — `{"error": str, "errors": [str]}` on fatal failure
4. **File size + OSError check** — `os.path.getsize()` before parse
5. **Root element check** — `root.tag != expected_root_tag` → return error dict
6. **itertext() for cell/paragraph text** — reliable text extraction

### New Work for FODT (~60%)

1. **List style detection** — `office:automatic-styles/text:list-style` scanning to build `list_style_map`
2. **Paragraph/heading extraction** — document-order traversal of `office:text` children
3. **List item extraction** — recursive `_collect_list_items()` for nested list support
4. **Table extraction** — `table:table → table:table-row → table:table-cell → text:p`
5. **Word count computation** — aggregate over paragraphs dict (after extraction)

---

## Key Observations

### office:automatic-styles
FODT documents contain style definitions in `office:automatic-styles` before the body. The prototype uses this section to determine list style types (bullet vs numbered). Other style attributes (paragraph styles, heading styles) are captured as `style_name` but not resolved — style resolution is a Gate 5 neutral model concern.

### List Style Detection
The list style lookup path:
1. `text:list` element has `text:style-name` attribute (e.g., `BulletList`)
2. `office:automatic-styles` contains `text:list-style` elements with `style:name="BulletList"`
3. The `text:list-style` element has children: `text:list-level-style-bullet` (→ "bullet") or `text:list-level-style-number` (→ "numbered")

Note: The `style:name` attribute on `text:list-style` is in the `style:` namespace but the attribute name (`style:name`) needs the style namespace prefix. In the samples, this appears as a plain attribute `style:name` because the `style` namespace is declared on the root element.

### Heading Outline Level
FODT uses `text:outline-level` attribute on `text:h` elements to convey heading depth (1 = H1, 2 = H2, etc.). This is a flat attribute — no lookup required.

### Table Column Declarations
`table:table-column` elements appear before `table:table-row` elements. The prototype skips them (only processes `table:table-row` children).

---

## Limitations (Acceptable at Gate 4)

| Limitation | Gate Resolved | Notes |
|---|---|---|
| Style inheritance not resolved | Gate 5 | style_name captured but not looked up |
| Text spans (text:span) | Gate 5+ | innerText includes span content (itertext) |
| Metadata (dc:title, dc:creator) | Gate 4 P2 — deferred | Not in Gate 3 samples |
| Nested tables | Gate 5+ | Outer table only |
| Repeated column declarations | Gate 5+ | table:number-columns-repeated ignored |
| Footnotes / endnotes | Gate 5+ | Not in Gate 3 samples |
| Section containers (text:section) | Gate 5+ | Content within sections parsed if direct child |

---

## Sample Analysis

### minimal-document.fodt
- 1 text:p paragraph ("Hello, World!")
- word_count = 2
- mime_type confirmed, version 1.3
- No lists, no tables, no headings

### headings-and-paragraphs.fodt
- 3 text:h headings: "Section One" (L1), "Subsection One A" (L2), "Section Two" (L1)
- 4 text:p paragraphs
- word_count = 29

### list-basic.fodt
- 2 text:list elements: BulletList (bullet), NumberedList (numbered)
- Bullet: 3 items ("First bullet item", "Second bullet item", "Third bullet item")
- Numbered: 3 items ("Step one", "Step two", "Step three")
- 2 surrounding text:p paragraphs ("Bullet list example:", "Numbered list example:")

### table-basic.fodt
- 1 table:table (Table1) with 3 rows × 2 columns
- Row 0: ["Name", "Value"]
- Row 1: ["Alpha", "100"]
- Row 2: ["Beta", "200"]
- 2 surrounding text:p paragraphs

---

## Self-Challenge

1. **Did I implement all P0 requirements (FR-001, FR-002, FR-003, FR-007)?** YES.
2. **Did I implement all P1 requirements (FR-004, FR-005, FR-006)?** YES.
3. **Did the validation pass 4/4?** YES — FODT_PROTOTYPE_VALIDATION: PASS.
4. **Is the parser free of unhandled exceptions?** YES — all exceptions caught and returned as error dicts.
5. **Did I create any product source?** NO — prototype in prototypes/by-format/fodt/ only.
6. **Did I use any third-party libraries?** NO — Python stdlib only (xml.etree.ElementTree, os, pathlib).
7. **Is the FODS reuse documented?** YES — ~40% reuse pattern documented above.
