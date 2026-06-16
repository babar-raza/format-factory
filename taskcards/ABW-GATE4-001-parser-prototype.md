# ABW-GATE4-001 — ABW Gate 4 Parser Prototype

**Created:** 2026-05-16 (R19)
**Status:** completed
**Priority:** MEDIUM
**Completed:** 2026-06-15 (verified: prototype + 14 tests pass)

## Scope

Create `prototypes/by-format/abw/abw_parser.py`:
- Parse flat XML ABW (abiword root, section/p/c structure)
- Extract: sections, paragraphs, text content, props attributes
- Corpus validation: 3 synthetic samples from samples/by-format/abw/

## Key Technical Notes

- File format: plain XML (.abw) or gzip-compressed (.abw.gz, .zabw)
- Root element: <abiword> with version/fileformat attributes
- Namespaces: fo, math, svg, dc, xlink (but often minimal in simple files)
- Props pattern: CSS-style props attribute (need simple parser)
- Images: Base64-encoded inline

## Gate 2 Note

Gate 2 was passed_with_notes — primary DTD (abisource.com) unreachable.
Implementation should reference AbiWord source code for format details.
AWML 1.0 is documented as "out-of-date" relative to current AbiWord.

## Prerequisites

- [x] ABW Gate 1: passed
- [x] ABW Gate 2: passed_with_notes (secondary sources)
- [x] ABW Gate 3: passed (3 synthetic samples)
- [x] Prototype: prototypes/by-format/abw/abw_parser.py
- [x] Gate 4 tests: tests/skills/test_abw_gate4_prototype.py (14 tests, all pass)
- [ ] DEC-034 IV: not done yet

## Test Plan

- PT-001: minimal-document.abw — section_count == 1, para_count == 1
- PT-002: two-paragraphs.abw — para_count == 2
- PT-003: empty-section.abw — section is empty (no paragraphs)
- PT-004: All 3 samples — no crash
