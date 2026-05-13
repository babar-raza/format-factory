# Fixture and Oracle Report — Commercial Load-Save Vertical Slice
# Lane G — COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
# Date: 2026-05-13

## Fixtures Created
| File | Format | Purpose |
|---|---|---|
| tests/net/fods/Fixtures/fods-minimal-roundtrip.fods | FODS | 1 sheet, 2 rows, mixed cells — roundtrip and edit tests |
| tests/net/fodt/Fixtures/fodt-minimal-roundtrip.fodt | FODT | 3 paragraphs + 1 heading — roundtrip and edit tests |

Both fixtures are project-owned synthetic, Apache-2.0.

## Oracle Strategy
LibreOffice not checked in this sprint. Structural comparison oracle used:
- XML parses successfully (DtdProcessing.Prohibit)
- ODF namespace preserved (contains office:document and MIME URI)
- Supported entity counts preserved (sheet/row/cell/paragraph counts)
- Edited value/text visible in saved XML and in reloaded model
- Save() output is non-empty (> 0 bytes, > original/2)

## Oracle Tests Created
| Test File | Tests | Result |
|---|---|---|
| tests/net/fods/FodsRoundtripOracleTests.cs | 7 | 7/7 PASS |
| tests/net/fodt/FodtRoundtripOracleTests.cs | 7 | 7/7 PASS |

## Key Oracle Checks
- OR-01: ODF namespace present in saved XML ✓
- OR-02: Save() produces non-empty file ✓
- OR-03: Edit changes output (edit not a no-op) ✓
- OR-04: Sheet/paragraph count stable through roundtrip ✓
- OR-05: Row/paragraph text stable ✓
- OR-06: Cell/heading flag stable ✓
- OR-07: LO_NOT_AVAILABLE documented (non-blocking) ✓

## LibreOffice Status
LO_NOT_AVAILABLE — LibreOffice oracle not run in this sprint.
Structural comparison provides sufficient oracle coverage for first vertical slice.
LO validation is planned for a future independent verification sprint.

## Lane G Verdict
LANE_G_PASS_WITH_LO_NOTE
