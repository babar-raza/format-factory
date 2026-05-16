# FODP-GATE4-001 — FODP Gate 4 Parser Prototype

**Created:** 2026-05-16 (R19)
**Status:** not_started
**Priority:** MEDIUM
**Blocker:** Requires R20+ implementation sprint prompt

## Scope

Create `prototypes/by-format/fodp/fodp_parser.py`:
- Parse flat-XML FODP (office:presentation namespace)
- Extract: slide count, slide names, title text per slide
- Corpus validation: 3 synthetic samples from samples/by-format/fodp/

## Prerequisites

- [x] FODP Gate 1: passed
- [x] FODP Gate 2: passed_fast_path (ODF 1.3 cached)
- [x] FODP Gate 3: passed (3 synthetic samples)
- [x] Parser notes: acquisition-packs/fodp/parser-notes.md
- [ ] Prototype: not created yet
- [ ] Gate 4 tests: not created yet
- [ ] DEC-034 IV: not done yet

## Key References

- Spec: .local/spec-cache/fods/1.3/ (shared ODF 1.3)
- Samples: samples/by-format/fodp/
- Parser notes: acquisition-packs/fodp/parser-notes.md
- FODS prototype (reference): prototypes/by-format/fods/fods_parser.py

## Test Plan

- PT-001: minimal-presentation.fodp — slide_count == 1
- PT-002: two-slides-basic.fodp — slide_count == 2
- PT-003: title-only.fodp — slide_count == 0
- PT-004: minimal-presentation.fodp — title text == "Hello"
