# TC-0060: Paragraph Style Preservation — FODT Python Writer

**ID:** TC-0060-paragraph-style-fodt
**Gap ID:** TC-PARASTYLE-001
**Status:** OPEN
**Priority:** Low
**Format:** FODT
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R52 or later

## Gap Description

Python FODT writer discards `text:style-name` attributes on `<text:p>` and `<text:h>`
elements. Paragraph styles (Body Text, Quote, Code, etc.) and automatic styles (per-paragraph
formatting overrides) are not emitted. Only the block type (paragraph vs heading) and
heading outline level are preserved.

Note: heading `text:outline-level` WAS fixed in R49 (writer fix for blocks key + headings).
This TC tracks the remaining style-name gap only.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fodt.md`
- Gap ID: TC-PARASTYLE-001
- R49 fix: `src/python/fodt/writer.py` now emits `text:outline-level` for headings.
  This partial fix does NOT close TC-PARASTYLE-001 (style-name still lost).

## Acceptance Criteria

1. `text:style-name` attributes are emitted on `<text:p>` elements when present in parse output.
2. `text:style-name` attributes are emitted on `<text:h>` elements when present in parse output.
3. `office:automatic-styles` section for paragraph styles is preserved verbatim.
4. At least 2 new tests covering paragraph style name round-trip.

## Fix Scope

- `src/python/fodt/parser.py`: verify `style_name` key is captured per block
- `src/python/fodt/writer.py`: emit `text:style-name="..."` when block has `style_name` key

## Note

LOW priority — cosmetic. Data content is preserved; only named styling is lost.
Python FOSS track focus is programmatic document generation, not visual fidelity.
