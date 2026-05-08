---
artifact_id: fodt-gate10-oss-scope
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate10-oss-scope.md
format_id: fodt
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
notes: "FODT Gate 10 OSS scope definition. run050."
---

# FODT Gate 10 -- OSS Scope Definition

**Gate:** 10 -- OSS Release Readiness (Planning)
**Format:** FODT
**Run:** run050 (2026-05-08)

---

## First OSS Release Scope

**Package:** format-factory-fodt v0.1.0 (name pending final Gate 10 approval)
**Tiers:** 0, 1, 2 (12 features)
**Language:** Python 3.11+
**License:** Apache-2.0

### Included Features

| Tier | Feature |
|------|---------|
| 0 | Parse root element, validate MIME type |
| 0 | Extract ODF version |
| 0 | Return structured error on invalid input |
| 0 | File size guard (100MB) |
| 1 | Extract paragraphs (text:p) |
| 1 | Extract headings (text:h) with outline level |
| 1 | Extract flat list items |
| 1 | Document statistics |
| 2 | Extract nested list structures (iterative) |
| 2 | Extract table structure |
| 2 | Detect unsupported elements |
| 2 | Neutral model output (7 entities) |

### Excluded Features (Deferred)

- Text spans / character formatting (Tier 3)
- Footnotes / endnotes (Tier 3)
- Document sections (Tier 3)
- Full layout rendering (Tier 4)
- Image / media extraction (Tier 4)
- Tracked changes (Tier 4)
- Macros / scripts (Tier 4)

---

## Source Layout (Future Sprint -- NOT Created Here)

    src/python/fodt/
        __init__.py
        parser.py          (main parse_fodt() entry point)
        neutral_model.py   (7-entity output model)
        constants.py       (namespace constants, MAX_FILE_BYTES)

---

## Core API (Proposed)

    parse_fodt(filepath: str | Path) -> dict

    Returns dict with keys:
        format_id: str           # "fodt"
        version: str             # ODF version e.g. "1.3"
        mime_type: str
        paragraphs: list[str]
        headings: list[dict]     # {level: int, text: str}
        lists: list[dict]        # nested list structure
        tables: list[dict]       # rows and cells
        errors: list[str]        # parse errors
        unsupported_features: list[str]

---

## Security Requirements

- IR-FODT-003: Iterative list traversal (TC-7)
- IR-FODT-002: 100MB file size guard
- IR-FODT-014: iterparse for large files
- IR-FODT-004: defusedxml optional (recommended)
- No network calls
- No file writes
