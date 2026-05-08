---
artifact_id: fodt-gate4-parser-prototype-plan
artifact_type: gate-planning
path: acquisition-packs/fodt/gate4-parser-prototype-plan.md
format_id: fodt
product_family: words
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
notes: "FODT Gate 4 parser prototype plan. Created run044 (2026-05-08) after Gate 3 PASSED. Planning only — execution requires explicit Gate 4 execution prompt."
---

# FODT Gate 4 — Parser Prototype Plan

**Format:** FODT — Flat OpenDocument Text
**Gate:** 4 — Parser Prototype
**Status:** planning_ready — Gate 3 PASSED; awaiting explicit Gate 4 execution prompt
**Created:** run044 (2026-05-08)
**Prerequisite:** Gate 3 PASSED (Babar Raza, 2026-05-08, run044)

---

## Gate 4 Objectives

Gate 4 creates a minimal viable parser prototype that:
1. Correctly parses all 4 Gate 3 FODT samples (4/4 PASS)
2. Extracts the primary document elements: paragraphs, headings, lists, tables
3. Returns a structured dict output suitable for neutral model mapping (Gate 5)
4. Handles XML errors safely (no unhandled exceptions)
5. Uses only Python stdlib (ElementTree) — no external dependencies at prototype stage

---

## Prototype Architecture

### File: `prototypes/by-format/fodt/fodt_parser.py`

**Primary function:**
```python
def parse_fodt(file_path: str) -> dict:
    """Parse a FODT file. Returns a dict with keys:
      - format_id: "fodt"
      - mime_type: str
      - version: str
      - paragraphs: list[dict]  # {text, style_name, outline_level (for headings)}
      - lists: list[dict]       # {items: list[{text, level}], list_style}
      - tables: list[dict]      # {name, rows: list[list[str]]}
      - word_count: int
      - errors: list[str]
    """
```

**Namespace map (reuse from FODS prototype):**
```python
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text":   "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table":  "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "style":  "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo":     "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "dc":     "http://purl.org/dc/elements/1.1/",
}
```

### File: `prototypes/by-format/fodt/validate_against_samples.py`

Runs parse_fodt() on each Gate 3 sample and asserts:
- No errors in result
- Expected structural elements present (paragraphs, headings, lists, tables as applicable)
- Output is deterministic (run twice, same result)

---

## FODS Reuse Analysis

| Component | FODS reuse | New work |
|---|---|---|
| XML parse entry point | Direct reuse (ElementTree.parse) | None |
| Namespace dict | Partial reuse (add text, fo, dc namespaces) | Add 3 namespaces |
| Error handling wrapper | Direct reuse (try/except ParseError) | None |
| Output dict structure | Pattern reuse (different keys) | New keys: paragraphs, lists, tables |
| validate_against_samples.py | Pattern reuse | New assertions per FODT structure |
| README.md + prototype-notes.md | Template reuse | FODT-specific content |

**Estimated reuse: ~40% of code (structure + plumbing). ~60% new work (text model logic).**

---

## Parser Requirements (FR-001 through FR-007)

See `acquisition-packs/fodt/parser-requirements.md` for full requirement specs.

| Req ID | Capability | Sample Coverage | Priority |
|---|---|---|---|
| FR-001 | Verify root element `office:document` and MIME type | All 4 | P0 |
| FR-002 | Extract `text:p` paragraph text content | minimal, headings | P0 |
| FR-003 | Extract `text:h` heading text + `text:outline-level` | headings-and-paragraphs | P0 |
| FR-004 | Extract `text:list` with bullet + numbered items | list-basic | P1 |
| FR-005 | Extract `table:table` rows and cells within text flow | table-basic | P1 |
| FR-006 | Compute document word count (all paragraphs) | all 4 | P1 |
| FR-007 | Return structured error on malformed XML (ParseError) | — | P0 |

---

## Validation Pass Criteria

Gate 4 PASSES when validate_against_samples.py reports:
```
PT-001: minimal-document.fodt — PASS
PT-002: headings-and-paragraphs.fodt — PASS
PT-003: list-basic.fodt — PASS
PT-004: table-basic.fodt — PASS
FODT_PROTOTYPE_VALIDATION: PASS 4/4
```

---

## Execution Gate

**Gate 4 execution is blocked until a human issues an explicit Gate 4 execution prompt.**

The execution prompt must state:
- TC-0034 authorized for Gate 4 parser prototype execution
- No product source creation (no src/python/fodt/, no src/net/fodt/)
- No neutral model (Gate 5)
- No Gate 4 self-approval
- TC-0035 DEC-034 verification required in a separate session after TC-0034
