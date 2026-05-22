# Phase Audit 5 Plan

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Target phase:** Phase 5 — Product Mapping / Implementation Authorization

## Phase 5 Scope

Phase 5 asks: Are the implemented FODS/FODT capabilities correct, complete, and
authorized for product use? It bridges from "parser exists and tests pass" to
"implementation is production-ready for the specified scope."

## Audit Dimensions

### 5.1 Product Feature Map

Map each implemented capability to its product track:

| Feature | Python FOSS | .NET Commercial | Status |
|---------|-------------|----------------|--------|
| FODS parse (all cell types) | Yes | Yes | Implemented |
| FODS write/save | Yes | Yes | Implemented |
| FODS formula preservation | Yes (R53) | TBD | Python: R53; .NET: not verified |
| FODS CSV export | Yes | Yes | Implemented (csv_exporter.py) |
| FODS XML export (workbook_to_xml) | Yes | n/a | Implemented |
| FODT parse (headings/lists/tables/paras) | Yes | Yes | Implemented |
| FODT write/save | Yes | Yes | Implemented |
| FODT heading preservation | No | No | R54 |
| FODT list preservation | No | No | R54+ |
| FODT table preservation | No | No | R54+ |
| FODT TXT export | Yes | TBD | R51 |
| FODT Markdown export | No | No | Future |

### 5.2 Object Model Scope

For Phase 5, verify that the object model boundary is documented:
- What is explicitly IN scope (Cell, Row, Sheet, Workbook; Para, Heading, List, Table)
- What is explicitly OUT of scope with warning behavior
- Merged cells (COVERED): warning emitted, content not preserved — correct
- Macros/scripts: detected, not executed, warning — correct
- Embedded images/charts (draw:frame): warning, not processed — correct

### 5.3 Unsupported Feature Disclosure

Verify that each "unsupported" feature:
- Emits a warning in the neutral model
- Does not silently drop data
- Is listed in `unsupported_features` field

### 5.4 Package Scope

For Phase 5, verify:
- Python FOSS packages include only what is tested
- No alpha/beta feature is labeled production-ready
- `__capability_level__ = "alpha-foss-preview"` — correct
- `commercial_product_ready = False` — correct

### 5.5 Gate Constraints

- Gate 11 G11-G: NOT approved — commercial release blocked until Babar Raza approval
- Phase 5 can be audited independently of G11-G approval

### 5.6 Readiness Boundaries

Phase 5 audit should declare:
- Python FOSS: Alpha-preview, suitable for testing only
- .NET Commercial: G11-E prototype, not production
- Neither track should claim production readiness

## Phase 5 Execution Plan

Phase 5 audit target: R54 sprint.

R54 prerequisites:
1. TC-0057 (FODT heading) closed
2. Unsupported-feature disclosure verified in tests
3. Product feature map complete
4. Object model boundary tests added (test each unsupported feature emits warning)

## Phase 5 Acceptance Criteria

- Feature map complete (all implemented features listed with track)
- Each unsupported feature has a warning test
- Object model boundary documented
- No false production-readiness claims
- Package `__capability_level__` and `commercial_product_ready` verified

**Phase 5 status as of R53:** NOT_STARTED (planned for R54)
