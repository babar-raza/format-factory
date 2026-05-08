---
artifact_id: fods-phase4-python-source-execution-plan
artifact_type: acquisition-pack
path: acquisition-packs/fods/phase4-python-source-execution-plan.md
format_id: fods
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
notes: "FODS Phase 4 Python FOSS source execution plan. Planning only. run050."
---

# FODS Phase 4 -- Python FOSS Source Execution Plan

**Format:** FODS
**Run:** run050 (2026-05-08)
**Status:** PLANNING ONLY -- no source created here

---

## Authorization Requirement

This plan is a planning document. No source is created.
Source creation requires an explicit Phase 4 Python FOSS implementation execution prompt.

---

## Future Source Path

    src/python/fods/

**DO NOT CREATE in this sprint.**

---

## FUL Input Files

| File | Purpose |
|------|---------|
| acquisition-packs/fods/format-profile.yaml | Format classification |
| acquisition-packs/fods/verified-facts.yaml | 20 spec-cited facts |
| acquisition-packs/fods/implementation-requirements.yaml | 20 requirements |
| acquisition-packs/fods/parser-strategy.yaml | 6 parser decisions |
| acquisition-packs/fods/security-surface.yaml | 8 threats/controls |
| acquisition-packs/fods/product-readiness.yaml | Tier map, authorization |

---

## Proposed Module Layout

    src/python/fods/
        __init__.py            (package init)
        parser.py              (parse_fods() main entry point)
        neutral_model.py       (6-entity output model validation)
        constants.py           (namespace constants, MAX_FILE_BYTES)
        exceptions.py          (FodsParseError, FodsSizeError)

---

## First API Surface

    parse_fods(filepath: str | Path) -> dict

    Returns:
        format_id: "fods"
        version: str
        mime_type: str
        sheets: list[dict]         # Sheet objects
        errors: list[str]          # XML parse errors
        unsupported_features: list[str]

    Raises:
        FodsSizeError:   if file > MAX_FILE_BYTES
        ValueError:      if filepath is invalid

---

## Implementation Requirements (Priority Order)

1. IR-FODS-001: Root parse, MIME validation, error dict
2. IR-FODS-020: Path validation before open
3. IR-FODS-003: 100MB file size guard
4. IR-FODS-017: parse_errors list from XML errors
5. IR-FODS-002: ET.iterparse streaming (TC-6 resolved)
6. IR-FODS-005: Sheet name extraction
7. IR-FODS-006: String cell values
8. IR-FODS-007: Typed values (float, boolean, date, time)
9. IR-FODS-009: Cell position tracking
10. IR-FODS-010: Row repeat expansion
11. IR-FODS-011: Column repeat expansion
12. IR-FODS-014: unsupported_features list
13. IR-FODS-015: draw:frame detection
14. IR-FODS-016: Macro detection
15. IR-FODS-018: Neutral model validation

Deferred (Tier 3): IR-FODS-008 (formulas), IR-FODS-013 (date/time detail)

---

## Test Strategy

    tests/python/fods/
        test_parser_basic.py      (Gate 3 samples: 4/4 PASS)
        test_parser_malformed.py  (Gate 7 fixtures: 18/18 PASS)
        test_parser_security.py   (file size guard, XXE protection)
        test_neutral_model.py     (6-entity model validation)

---

## Security Controls

1. iterparse (no full-document memory load)
2. 100MB file size guard before open
3. defusedxml optional import (recommended)
4. No network calls
5. No file writes
6. Expat DOCTYPE rejection (implicit)

---

## Release Blockers

1. Explicit Phase 4 Python implementation execution prompt (not yet issued)
2. IR-FODS-002 (iterparse) must be implemented
3. All Gate 3 sample tests must pass
4. All Gate 7 malformed fixture tests must pass
5. Neutral model validation must pass

---

## Source Sprint Acceptance Criteria

1. src/python/fods/ exists with all 5 module files
2. parse_fods() handles all 4 Gate 3 samples (4/4 PASS)
3. parse_fods() handles all 18 Gate 7 fixtures (18/18 PASS)
4. File size guard rejects > 100MB files
5. iterparse used (no ET.parse() in parser.py)
6. Neutral model output validates against 6-entity schema
7. No unhandled exceptions on any input
8. Evidence bundle validates BUNDLE_VALIDATION: PASS
