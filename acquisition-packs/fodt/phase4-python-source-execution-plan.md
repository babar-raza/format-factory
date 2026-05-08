---
artifact_id: fodt-phase4-python-source-execution-plan
artifact_type: acquisition-pack
path: acquisition-packs/fodt/phase4-python-source-execution-plan.md
format_id: fodt
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
notes: "FODT Phase 4 Python FOSS source execution plan. Planning only. run050."
---

# FODT Phase 4 -- Python FOSS Source Execution Plan

**Format:** FODT
**Run:** run050 (2026-05-08)
**Status:** PLANNING ONLY -- no source created here

---

## Authorization Requirement

This plan is a planning document. No source is created.
Source creation requires an explicit Phase 4 Python FOSS implementation execution prompt.
Gate 10 planning is complete (run050); full Gate 10 code-complete approval requires Phase 4 sprint.

---

## Future Source Path

    src/python/fodt/

**DO NOT CREATE in this sprint.**

---

## FUL Input Files

| File | Purpose |
|------|---------|
| acquisition-packs/fodt/format-profile.yaml | Format classification |
| acquisition-packs/fodt/verified-facts.yaml | 15 spec-cited facts |
| acquisition-packs/fodt/implementation-requirements.yaml | 15 requirements |
| acquisition-packs/fodt/parser-strategy.yaml | 5 parser decisions |
| acquisition-packs/fodt/security-surface.yaml | 8 threats/controls |
| acquisition-packs/fodt/product-readiness.yaml | Tier map, authorization |

---

## Proposed Module Layout

    src/python/fodt/
        __init__.py
        parser.py              (parse_fodt() main entry point)
        list_traversal.py      (iterative list traversal -- TC-7 required)
        neutral_model.py       (7-entity output model)
        constants.py
        exceptions.py

---

## First API Surface

    parse_fodt(filepath: str | Path) -> dict

    Returns:
        format_id: "fodt"
        version: str
        mime_type: str
        paragraphs: list[str]
        headings: list[dict]       # {level: int, text: str}
        lists: list[dict]          # nested structure (iterative)
        tables: list[dict]
        errors: list[str]
        unsupported_features: list[str]

---

## Key Implementation Constraints

1. IR-FODT-003: Iterative list traversal (TC-7) -- REQUIRED, not optional
2. IR-FODT-014: ET.iterparse (TC-6) -- REQUIRED for product source
3. IR-FODT-002: 100MB file size guard
4. No network calls, no file writes

---

## Test Strategy

    tests/python/fodt/
        test_parser_basic.py      (Gate 3 samples: 4/4 PASS)
        test_parser_malformed.py  (Gate 7 fixtures: 18/18 PASS)
        test_list_traversal.py    (deep nesting Gate 7 c03)
        test_neutral_model.py     (7-entity model)

---

## Release Blockers

1. Explicit Phase 4 Python FODT implementation execution prompt
2. Iterative list traversal implementation (IR-FODT-003, TC-7)
3. iterparse migration (IR-FODT-014, TC-6)
4. Gate 10 code-complete approval (requires full Phase 4 sprint)

---

## Reuse from FODS Python Implementation

- constants.py (namespace constants, MAX_FILE_BYTES) -- ~80% reuse
- Error dict pattern -- 100% reuse
- File size guard -- 100% reuse
- Security controls -- 100% reuse
- Test structure -- 100% reuse
