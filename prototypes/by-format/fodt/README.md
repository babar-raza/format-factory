---
artifact_id: fodt-prototype-readme
artifact_type: prototype
path: prototypes/by-format/fodt/README.md
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
notes: "FODT Gate 4 prototype README. Created run045 (2026-05-08). Validation 4/4 PASS."
---

# FODT Parser Prototype — Gate 4

**Format:** Flat OpenDocument Text (FODT)
**Gate:** 4 (Parser Prototype)
**Created:** 2026-05-08 (run045)
**Status:** VALIDATED — 4/4 PASS (PT-001..PT-004)

---

## Purpose

This is the Gate 4 prototype parser for the FODT format. It is not product source code.
Its purpose is to demonstrate that the format is parseable using Python stdlib (ElementTree)
and to validate the 4 Gate 3 FODT samples before Gate 4 human approval.

## Files

| File | Purpose |
|---|---|
| `fodt_parser.py` | Core parser — `parse_fodt(filepath)` |
| `validate_against_samples.py` | Gate 4 validation script (PT-001..PT-004) |
| `prototype-notes.md` | Coverage, assumptions, limitations |

## Usage

```bash
# Validate all 4 Gate 3 samples
python prototypes/by-format/fodt/validate_against_samples.py

# Parse a single file
python prototypes/by-format/fodt/fodt_parser.py samples/by-format/fodt/minimal-document.fodt
```

## Parser Return Structure

`parse_fodt(filepath: str) -> dict`

```python
{
  "mime_type":  str,          # office:mimetype attribute
  "version":    str,          # office:version attribute
  "paragraphs": [             # text:p and text:h elements (document order)
    {
      "element":       "paragraph" | "heading",
      "text":          str,
      "style_name":    str,
      "outline_level": int | None,  # int for headings, None for paragraphs
    },
    ...
  ],
  "lists": [                  # text:list elements
    {
      "element":    "list",
      "list_style": "bullet" | "numbered" | "unknown",
      "items": [
        {"text": str, "level": int},
        ...
      ],
    },
    ...
  ],
  "tables": [                 # table:table elements
    {
      "element": "table",
      "name":    str,
      "rows":    [[str, ...], ...],  # row-major cell text
    },
    ...
  ],
  "word_count": int,           # total words in paragraphs + headings
  "errors":     [str],         # non-fatal issues (empty = clean parse)
}
```

On fatal error (XML parse failure, wrong root element):
```python
{
  "error":  str,
  "errors": [str],
}
```

## NOT Product Source

This prototype is for format exploration and Gate 4 validation only.
Product source lives in `src/python/fodt/` (Gate 10+, not yet authorized).

## FODS Reuse

Approximately 40% of this parser reuses the FODS prototype pattern:
- Namespace handling (Clark notation `{uri}local`)
- MAX_FILE_BYTES guard (100 MB)
- Error return model (no raised exceptions)
- File size check + XML parse guard
- Root element verification

New work: paragraph/heading extraction, list style detection via automatic-styles,
table extraction, word count computation.
