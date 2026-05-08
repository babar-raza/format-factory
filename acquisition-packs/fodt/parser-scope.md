---
artifact_id: fodt-parser-scope
artifact_type: acquisition-pack
path: acquisition-packs/fodt/parser-scope.md
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
notes: "FODT parser scope. Created run044 (2026-05-08) after Gate 3 PASSED. Gate 4 parser prototype planning."
---

# FODT Parser Scope — Gate 4

**Format:** Flat OpenDocument Text (FODT)
**Gate:** Gate 4 (Parser Prototype)
**Created:** run044 (2026-05-08)

---

## In Scope — Gate 4 Prototype

| Element | ODF 1.3 Section | Parser action |
|---|---|---|
| `office:document` root | §2 | Verify root + MIME type |
| `office:body / office:text` | §2 | Navigate to primary content |
| `text:p` paragraphs | §5.1 | Extract text content |
| `text:h` headings | §3.1, §5.3 | Extract text + outline-level |
| `text:list` / `text:list-item` | §5.3 | Extract list items with level |
| `table:table` (in text flow) | §14 | Extract rows and cells |
| `text:list-level-style-bullet` | §14.10 | Identify bullet lists |
| `text:list-level-style-number` | §14.11 | Identify numbered lists |
| Malformed XML error handling | — | Catch ParseError, return error dict |
| Deep nesting RecursionError | — | Catch RecursionError, return error dict |

---

## Out of Scope — Gate 4 Prototype

| Element | Earliest Gate | Reason |
|---|---|---|
| Style inheritance resolution | Gate 5 | Neutral model defines style mapping |
| `text:span` character styles | Gate 5 | Character-level detail |
| `office:automatic-styles` full resolution | Gate 5 | Complex; neutral model defines coverage |
| `office:styles` named style lookup | Gate 5 | Style resolution system |
| Embedded images (`draw:frame`, `draw:image`) | Gate 5+ | Binary content out of scope |
| Comments / annotations (`text:note`) | Gate 5+ | Low priority |
| Change tracking | Gate 5+ | ODF tracked changes model |
| Metadata (`dc:title`, `dc:creator`, `dc:date`) | Gate 4 optional P2 | Nice to have |
| Formula content in text | Gate 5+ | Not present in Gate 3 samples |
| Master pages | Gate 5+ | Page layout model |

---

## What Is NOT Built at Gate 4

Per AGENTS.md and GOVERNANCE.md:

| Item | Gate |
|---|---|
| Product source (`src/python/fodt/`, `src/net/fodt/`) | Gate 10 |
| Neutral model (`schemas/neutral-model/fodt/`) | Gate 5 |
| Oracle comparison | Gate 6 |
| Security audit | Gate 8 |
| FODT parser fuzz testing | Gate 7 |
| CI workflows | Gate 10+ |

---

## FODS Pipeline Reuse

| FODS component | FODT reuse |
|---|---|
| `fods_parser.py` top-level parse entry point | Pattern reuse (replace content model) |
| Namespace dictionary | Partial reuse (add text, fo, dc; keep office, table, style) |
| Error handling (try/except ParseError) | Direct reuse |
| `validate_against_samples.py` structure | Pattern reuse (replace assertions) |
| `prototype-notes.md` template | Template reuse |

Estimated effort: ~40% reuse from FODS Gate 4.
