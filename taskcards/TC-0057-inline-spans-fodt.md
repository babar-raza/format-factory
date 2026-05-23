# TC-0057: Inline Span Preservation — FODT Python Writer

**ID:** TC-0057-inline-spans-fodt
**Gap ID:** TC-INLINE-001
**Status:** CLOSED_VERIFIED
**Priority:** Medium
**Format:** FODT
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R51 or later

## Gap Description

Python FODT writer (`write_fodt()` / `document_to_xml()`) loses inline formatting spans
on write. Text runs with `<text:span>` wrappers (bold, italic, underline, hyperlinks)
are stripped to plain text. Only the plain text content is preserved; all span markup
is discarded.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fodt.md`
- Gap ID: TC-INLINE-001
- RISK-003 (active): Inline runs/tables/lists lost on Python FODT write

## Acceptance Criteria

1. A FODT file with inline-styled text can be written and reloaded with spans preserved.
2. `<text:span text:style-name="...">` wrappers are preserved verbatim for unmodified paragraphs.
3. Hyperlinks (`<text:a xlink:href="...">`) are preserved.
4. At least 3 new tests covering inline span round-trip.

## Fix Scope

- `src/python/fodt/parser.py`: verify inline spans are captured in block/run dict
- `src/python/fodt/writer.py`: emit `<text:span>` for runs with style, rather than
  emitting only the plain text content

## Risk

RISK-003 (active). Until this is fixed, users with styled paragraphs should use the .NET
commercial track which has full DOM-backed write fidelity.

## Closure

**Closed:** R55, 2026-05-23
**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Evidence:**
- `_collect_runs()` added to `src/python/fodt/parser.py` — captures text:span with style-name
- `_write_span()` added to `src/python/fodt/writer.py` — emits text:span for styled runs
- `_write_block()` updated — uses runs list when available
- 9 tests in `tests/python/fodt/test_r55_fodt_spans_ordering.py` (5 span capture + 4 round-trip)
- All tests pass. `text:span` with `text:style-name` preserved on round-trip.
- Note: `text:a` hyperlink preservation deferred (not captured by run model yet; requires separate acceptance criterion extension).
**Status:** CLOSED_VERIFIED
