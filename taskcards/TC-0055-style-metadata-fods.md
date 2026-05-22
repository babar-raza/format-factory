# TC-0055: Style Metadata Preservation — FODS Python Writer

**ID:** TC-0055-style-metadata-fods
**Gap ID:** TC-STYLE-001
**Status:** OPEN
**Priority:** Low
**Format:** FODS
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R52 or later

## Gap Description

Python FODS writer loses `office:styles` and `office:automatic-styles` sections on write.
Cell formatting (font, color, number format), column widths, row heights, and named styles
are all discarded. The output has no style definitions.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fods.md`
- Gap ID: TC-STYLE-001
- The Python writer emits a minimal FODS skeleton without any `<office:styles>` block.

## Acceptance Criteria

1. When round-tripping a FODS file that contains style definitions, the `<office:styles>`
   and `<office:automatic-styles>` sections are preserved verbatim in the output.
2. Cell `table:style-name` attributes are preserved for unmodified cells.
3. At least 2 new tests covering style round-trip.

## Fix Scope

- `src/python/fods/writer.py`: capture and re-emit styles block from parse output
- `src/python/fods/parser.py`: verify styles block is captured during parse

## Note

Style metadata preservation is tracked as LOW priority because the Python FOSS track
is primarily intended for data extraction and programmatic creation, not visual formatting
fidelity. The .NET commercial track handles full style fidelity.
