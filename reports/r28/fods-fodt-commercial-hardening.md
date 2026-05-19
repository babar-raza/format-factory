# R28 Lane H: FODS/FODT Commercial Capability Hardening Audit

- **Sprint:** R28
- **Lane:** H
- **Date:** 2026-05-19
- **Gate 11 status:** commercial_readiness_in_progress (G11-G NOT_STARTED)
- **commercial_product_ready:** false

## 1. Audit Scope

Audited FODS and FODT .NET commercial source and test suites against the commercial
capability model levels C4 through C9. Added C9 malformed-input resilience tests.

## 2. Source Files Audited

### FODS (src/net/fods/)
| File | Purpose | Lines |
|------|---------|-------|
| FodsDocument.cs | DOM-backed Load/Save, Sheets accessor, MimeType/OdfVersion | 167 |
| FodsParser.cs | Streaming Tier 0 parser, FodsParseResult | 287 |
| FodsWriter.cs | XDocument-to-file writer (UTF-8, no BOM) | 57 |
| FodsCsvExporter.cs | G11-E CSV exporter (first sheet) | 224 |
| FodsJsonExporter.cs | G11-E JSON exporter (all sheets) | 189 |
| FodsHtmlExporter.cs | G11-E HTML table exporter (all sheets) | 197 |
| Model/FodsCell.cs | Cell wrapper: Value, SetText, IsCovered | 75 |
| Model/FodsRow.cs | Row wrapper: Cells collection | 49 |
| Model/FodsSheet.cs | Sheet wrapper: Name, Rows collection | 50 |

### FODT (src/net/fodt/)
| File | Purpose | Lines |
|------|---------|-------|
| FodtDocument.cs | DOM-backed Load/Save, Body/Paragraphs accessor | 161 |
| FodtParser.cs | Streaming Tier 0 parser, FodtParseResult | 321 |
| FodtWriter.cs | XDocument-to-file writer (UTF-8, no BOM) | 56 |
| FodtTxtExporter.cs | G11-E TXT exporter | 171 |
| FodtMarkdownExporter.cs | G11-E Markdown exporter (ATX headings) | 191 |
| FodtHtmlExporter.cs | G11-E HTML exporter | 198 |
| Model/FodtParagraph.cs | Paragraph wrapper: Text, SetText, IsHeading, OutlineLevel | 81 |
| Model/FodtBody.cs | Body wrapper: Paragraphs collection | 51 |

## 3. Capability Model Assessment

### C4: Basic Load/Parse -- PASS

Both FODS and FODT implement:
- File-size guard (50 MB default, configurable)
- DTD prohibition (DtdProcessing.Prohibit) -- XXE defense
- XmlResolver disabled
- Empty-file rejection
- FodsParser (streaming) and FodsDocument.Load (DOM) dual paths
- FodtParser (streaming) and FodtDocument.Load (DOM) dual paths
- Proper exception wrapping (FodsDocumentException, FodtDocumentException)

Test coverage: FodsParserTests (12 tests), FodtParserTests (12 tests), plus
FodsDocumentRoundtripTests, FodtDocumentRoundtripTests.

### C5: Edit (Add/Modify Cells/Paragraphs) -- PASS

- FodsCell.SetText: updates text:p child, sets office:value-type="string"
- FodtParagraph.SetText: replaces all child content with text node
- Both throw ArgumentNullException on null input
- DOM-backed: mutations write through to the document

Test coverage: FodsDocumentEditTests (10 tests), FodtDocumentEditTests (10 tests).

### C6: Save/Export -- PASS

Save:
- FodsWriter/FodtWriter: UTF-8 no BOM, XML declaration, indent, parent-dir auto-create
- Preserves all DOM nodes (unknown elements survive)

Export (G11-E prototype):
- FODS: CSV (RFC 4180), JSON (typed envelope), HTML (table with escaping)
- FODT: TXT (plain text), Markdown (ATX headings), HTML (semantic tags)
- All exporters: UTF-8 no BOM, LF line endings, HTML escaping where needed
- All exporters: proper error handling, result types with status/warnings

Test coverage: FodsCsvExporterTests, FodsJsonExporterTests, FodsHtmlExporterTests,
FodtTxtExporterTests, FodtMarkdownExporterTests, FodtHtmlExporterTests.

### C7: Round-Trip Preservation -- PASS

- Load -> edit -> save -> reload: edited values persist, unedited values survive
- Sheet/paragraph count, names, MimeType, OdfVersion all preserved
- Double round-trip verified
- Multi-sheet editing does not corrupt other sheets

Test coverage: FodsC7C8RoundtripPreservationTests (10 C7 tests + 6 C8 tests),
FodtC7C8RoundtripPreservationTests (9 C7 tests + 7 C8 tests).

### C8: Cross-Format (Opaque Node Preservation) -- PASS

The DOM-backed strategy inherently preserves all unrecognized XML elements. Tests verify:
- Custom namespace elements survive edit round-trip
- office:automatic-styles survive round-trip
- dc:title metadata survives round-trip
- Custom attributes survive round-trip
- No node duplication after edit

Covered by C7/C8 test files above.

### C9: Malformed Input Resilience -- HARDENED (this sprint)

Pre-existing coverage (G11-F):
- FodsG11fMalformedXmlGuardTests: 8 parser-level tests
- FodtG11fHeadingAndGuardTests: 3 document-level guard tests + 5 heading tests

**New tests added (R28 Lane H):**

FODS (5 new tests in FodsG11fMalformedXmlGuardTests):
1. C9-MAL-FODS-01: Empty XML (valid XML, no ODF structure) -- loads with 0 sheets
2. C9-MAL-FODS-02: Missing office:spreadsheet -- loads with 0 sheets, MimeType readable
3. C9-MAL-FODS-03: Truncated XML file -- throws FodsDocumentException with "XML parse error"
4. C9-MAL-FODS-04: Parser on missing spreadsheet -- returns success + warning
5. C9-MAL-FODS-05: CSV exporter on no-sheets FODS -- exports empty CSV gracefully

FODT (5 new tests in FodtG11fHeadingAndGuardTests):
1. C9-MAL-FODT-01: Empty XML (valid XML, no ODF structure) -- Body null, Paragraphs empty
2. C9-MAL-FODT-02: Missing office:body -- Body null, Paragraphs empty, MimeType readable
3. C9-MAL-FODT-03: Truncated XML file -- throws FodtDocumentException with "XML parse error"
4. C9-MAL-FODT-04: Parser on missing body -- returns success with 0 paragraphs
5. C9-MAL-FODT-05: TXT exporter on empty body -- exports empty file gracefully

## 4. Test Results

```
FODS: Passed! - Failed: 0, Passed: 157, Skipped: 0, Total: 157
FODT: Passed! - Failed: 0, Passed: 145, Skipped: 0, Total: 145
```

Combined: 302 tests, 0 failures.

Previous baseline (R25): FODS 120/120, FODT 108/108.
Delta: FODS +37 (R27/R28 C7/C8/C9 tests), FODT +37 (R27/R28 C7/C8/C9 tests).

## 5. Security Posture

Both FODS and FODT maintain:
- DTD prohibition (DtdProcessing.Prohibit) in all XML reader paths
- XmlResolver = null (prevents external entity resolution)
- File-size guard (configurable, default 50 MB)
- Empty-file rejection (0 bytes)
- HTML output uses WebUtility.HtmlEncode for all user-controlled content
- JSON output uses System.Text.Json (no custom serialization vulnerabilities)
- CSV output uses RFC 4180 escaping

No security deficiencies found.

## 6. Findings and Gaps

### No Defects Found
All source code is structurally sound. Exception handling, null checks, and
boundary conditions are properly handled.

### Known Limitations (prototype-level, documented in source)
- table:number-columns-repeated not expanded in exports
- No formula evaluation engine
- FODS CSV exports first sheet only (by design for prototype)
- FODT inline formatting (bold/italic) stripped to plain text on edit
- FODT tables/frames/annotations not extracted by exporters
- No merged-cell colspan/rowspan in HTML output

### What Remains for G11-G
- G11-G: human approval required (Babar Raza) -- NOT_STARTED
- commercial_product_ready must remain false until G11-G is approved
- C7+ capability level requires full sub-gate evidence and human sign-off

## 7. Governance Assertions

- **commercial_product_ready: false** -- unchanged, correct
- **Gate 11 status: g11f_hardening_in_progress** -- G11-G NOT_STARTED
- This audit does NOT claim G11-G readiness
- All new tests follow existing patterns and conventions
- No new source files created; tests added to existing test files only

## 8. Files Modified

- `tests/net/fods/FodsG11fMalformedXmlGuardTests.cs` -- +5 C9 malformed-input tests
- `tests/net/fodt/FodtG11fHeadingAndGuardTests.cs` -- +5 C9 malformed-input tests
