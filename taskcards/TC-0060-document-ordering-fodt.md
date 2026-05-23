# TC-0060: Document Ordering — FODT Python Writer

**ID:** TC-0060-document-ordering-fodt
**Gap ID:** TC-ORDER-001
**Status:** CLOSED_VERIFIED
**Priority:** High
**Format:** FODT
**Track:** Python FOSS
**Sprint origin:** R54 (Phase Audit 5 identified as no-TC gap)
**Sprint target:** R55

## Gap Description

Python FODT neutral model stored blocks, lists, and tables as separate sequences.
The writer emitted them in fixed order (blocks → lists → tables) regardless of
the original document order. A document where a list appears between two paragraphs
would have all paragraphs emitted first, then the list — losing the original order.

## Evidence

- Phase Audit 5 report: `reports/r54/phase-audit-5-product-mapping.md` — identified as "No TC"
- FODT neutral model: `blocks`, `lists`, `tables` stored as separate lists in `build_document()`
- Writer R54 docstring: "Known limitation: document ordering between blocks, lists, and tables is not preserved"

## Acceptance Criteria

1. Parser produces a `content` key in the neutral model — a unified document-order sequence.
2. Writer uses `content` sequence when present, emitting elements in document order.
3. A paragraph → list → paragraph document round-trips with paragraph order preserved.
4. A paragraph → table → paragraph document round-trips with paragraph order preserved.
5. Backward compatibility: documents without `content` key still serialize correctly.

## Fix Scope

- `src/python/fodt/parser.py`: add `content: list = []`; append `{"kind": "block"|"list"|"table", "data": <item>}` in `_handle_text_child`
- `src/python/fodt/neutral_model.py`: add `content` parameter to `build_document()`; include in returned dict
- `src/python/fodt/writer.py`: check for `content` in `document_to_xml()`; use it when present; fall back to legacy path

## Closure

**Closed:** R55, 2026-05-23
**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Evidence:**
- `content` list added to `_parse_streaming()` in `src/python/fodt/parser.py`
- `neutral_model.build_document()` accepts and stores `content` parameter
- `document_to_xml()` dispatches from `content` when present
- 5 ordering tests in `tests/python/fodt/test_r55_fodt_spans_ordering.py`
- All 14 new tests PASS; all 234 existing FODT tests PASS (zero regressions)
**Status:** CLOSED_VERIFIED
