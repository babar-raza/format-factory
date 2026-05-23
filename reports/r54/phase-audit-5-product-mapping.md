# Phase Audit 5: Product Mapping

**Sprint:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
**Date:** 2026-05-23
**Auditor:** R54 agent

## Scope

Phase Audit 5 covers product capability mapping across both FODS and FODT formats,
including write capability advancement since Phase Audit 4.

## FODS Product Capability Map (R54)

| Capability | Status | Evidence |
|-----------|--------|----------|
| Parse (read) | PASS | src/python/fods/parser.py; R50 tests |
| Neutral model | PASS | fods_schema.json |
| Write/export XML | PASS | src/python/fods/writer.py |
| Float cell values | PASS | _write_cell() float branch |
| Boolean cell values | PASS | _write_cell() boolean branch |
| String cell values | PASS | _write_cell() string branch |
| Formula preservation (TC-0054) | CLOSED_VERIFIED (R53) | test_r53_formula_preservation.py 7/7 |
| Styles/merged cells | NOT_IMPLEMENTED | R55+ |
| .NET round-trip | PASS (POC) | R51 MT4 |

## FODT Product Capability Map (R54)

| Capability | Status | Evidence |
|-----------|--------|----------|
| Parse (read) | PASS | src/python/fodt/parser.py; R50 tests |
| Neutral model | PASS | fodt_schema.json |
| Write/export XML | PASS | src/python/fodt/writer.py |
| Paragraph blocks | PASS | _write_block() text:p |
| Heading blocks (TC-0057 predecessor) | PASS (R49) | test_r54_fodt_preservation.py 5/5 |
| List preservation (TC-0059) | PARTIAL_PASS (R54) | _write_list(); 7 tests PASS |
| Table preservation (TC-0058) | PARTIAL_PASS (R54) | _write_table(); 8 tests PASS |
| Inline span preservation (TC-0057) | OPEN | Not implemented; test documents OPEN |
| Document ordering (blocks+lists+tables) | KNOWN_LIMITATION | Separate sequences; R55 deferred |
| .NET round-trip | PASS (POC) | R51 MT4 |

## Summary Delta: Phase Audit 4 → Phase Audit 5

| Change | Detail |
|--------|--------|
| TC-0054 closed | FODS formula preservation CLOSED_VERIFIED in R53 |
| TC-0059 advanced | FODT list preservation PARTIAL_PASS in R54 |
| TC-0058 advanced | FODT table preservation PARTIAL_PASS in R54 |
| FODT heading truth repaired | Heading preservation confirmed PASS since R49 |
| Sidecar enforcement | Fail-closed sidecar protocol implemented in validator |
| Artifact policy | Explicit none/external_ref/self_contained in contracts |
| Formula docstring | FODS writer.py updated to document TC-0054 |

## Open Gaps (Phase Audit 5)

| Gap | TC | Priority |
|-----|-----|----------|
| FODT inline span preservation | TC-0057 | HIGH (affects rich text round-trip) |
| FODT document ordering | No TC | MEDIUM (separate block/list/table sequences) |
| Styles/merged cells (FODS) | No TC | LOW (not blocking for FOSS tier) |

## Phase Audit 5 Verdict

**CONDITIONAL_PASS_WITH_FODT_GAPS**

- FODS: full PASS (formula preservation closed R53)
- FODT headings: PASS (corrected R53 false claim)
- FODT lists: PARTIAL_PASS (R54 advance — ordering limitation)
- FODT tables: PARTIAL_PASS (R54 advance — ordering limitation)
- FODT inline spans: OPEN — deferred to R55
- Sidecar enforcement: PASS (fail-closed)
- Artifact policy: PASS (explicit none/external_ref/self_contained)

## Next Phase (R55) Prerequisites

To achieve full Phase 5 PASS:
1. TC-0057: Implement inline span preservation (parser + writer changes)
2. Fix document ordering: merge blocks/lists/tables into single document-order sequence in neutral model
3. Promote PARTIAL_PASS for TC-0058/TC-0059 to PASS once ordering is fixed
