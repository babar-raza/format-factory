# FODG-GATE4-001 — FODG Gate 4 Parser Prototype

**Created:** 2026-05-16 (R19)
**Status:** completed
**Priority:** MEDIUM
**Blocker:** Requires R20+ implementation sprint prompt

## Scope

Create `prototypes/by-format/fodg/fodg_parser.py`:
- Parse flat-XML FODG (office:drawing + draw: namespace)
- Extract: page count, page names, shape types per page
- Corpus validation: 3 synthetic samples from samples/by-format/fodg/

## Prerequisites

- [x] FODG Gate 1: passed
- [x] FODG Gate 2: passed_fast_path (ODF 1.3 cached)
- [x] FODG Gate 3: passed (3 synthetic samples)
- [x] Parser notes: acquisition-packs/fodg/parser-notes.md
- [ ] Prototype: not created yet
- [ ] Gate 4 tests: not created yet
- [ ] DEC-034 IV: not done yet

## Key References

- Spec: .local/spec-cache/fods/1.3/ (shared ODF 1.3)
- Samples: samples/by-format/fodg/
- Parser notes: acquisition-packs/fodg/parser-notes.md
- FODS prototype (reference): prototypes/by-format/fods/fods_parser.py

## Commercial Track Note

Aspose.Imaging LOAD_ONLY for FODG — round-trip save not confirmed.
Gate 6+ investigation required before commercial track planning.

## Test Plan

- PT-001: minimal-drawing.fodg — page_count == 1
- PT-002: shapes-basic.fodg — shapes count == 3
- PT-003: empty-page.fodg — shapes == []
- PT-004: minimal-drawing.fodg — shapes[0].type == "rect"
