# FODS Load/Save Roundtrip Implementation Report
# Lane C — COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
# Date: 2026-05-13

## Files Created
- src/net/fods/FodsDocument.cs — DOM-backed document model
- src/net/fods/FodsWriter.cs — XML writer (internal)
- src/net/fods/Model/FodsSheet.cs — sheet wrapper
- src/net/fods/Model/FodsRow.cs — row wrapper
- src/net/fods/Model/FodsCell.cs — cell wrapper
- tests/net/fods/Fixtures/fods-minimal-roundtrip.fods — test fixture
- tests/net/fods/FodsDocumentRoundtripTests.cs — 13 roundtrip tests

## Design Decisions
1. DOM-backed with XDocument (System.Xml.Linq) — full preservation of unknown nodes
2. Format-local namespace (FormatFactory.Fods) — no shared core
3. Security: DtdProcessing.Prohibit, XmlResolver=null, 50 MB file size guard
4. FodsDocument is immutable after construction; Save() writes full XDocument

## API Implemented
- FodsDocument.Load(string path, long maxFileSizeBytes = 50MB)
- FodsDocument.Save(string path)
- FodsDocument.Sheets — IReadOnlyList<FodsSheet>
- FodsDocument.MimeType, OdfVersion
- FodsSheet.Name (get/set), Rows
- FodsRow.Cells
- FodsCell.Value (get), IsCovered

## ODF Spec Basis
- §3.1.2 office:document root
- §9.4.2 table:table
- §9.4.4 table:table-row
- §9.4.5 table:table-cell / covered-table-cell
- §6.1.1 text:p

## Test Results
- 13 roundtrip tests: 13/13 PASS
- Also covers: null path, missing file, DTD, size guard, XML validity, ODF namespace, save is not no-op

## Existing API Compatibility
FodsParser.Parse() unchanged. FodsParserTests.cs: 12/12 PASS.

## Lane C Verdict
LANE_C_PASS_FODS_ROUNDTRIP
