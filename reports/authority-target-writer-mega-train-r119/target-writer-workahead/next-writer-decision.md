# Next Writer Decision
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001
Lane: E

## Discovery

All four target writers are ALREADY BUILT and ALREADY WIRED to their exporters:

| Writer | Library | Exporter | Wired | Tests |
|--------|---------|---------|-------|-------|
| FormatFactory.Csv | src/net/csv/ | FodsCsvExporter.cs | YES | 15/15 PASS |
| FormatFactory.Html | src/net/html/ | FodsHtmlExporter.cs | YES | 12/12 PASS |
| FormatFactory.Txt | src/net/txt/ | FodtTxtExporter.cs | YES | 8/8 PASS |
| FormatFactory.Markdown | src/net/markdown/ | FodtMarkdownExporter.cs | YES | 11/11 PASS |

**Total target writer tests: 46/46 PASS**

This sprint's LANE E objective is ALREADY MET by the previous sprint.

## Next Phase Decisions

Since all writers are built and wired, the next logical steps are:

### Option 1: RCA Proof Wiring (HIGHEST PRIORITY)
Wire each export capability claim in the RCA proof graph to:
- The writer library node
- The exporter node
- The test nodes
- The dogfood artifact nodes

This would change: FODS PARTIAL → FODS READY (CSV + HTML)
This would change: FODT PARTIAL → FODT READY (TXT + Markdown)

### Option 2: FODT HTML Export (NEW CAPABILITY)
FODT → HTML is not yet implemented. Would require:
1. New FodtHtmlExporter.cs using FormatFactory.Html.HtmlWriter
2. Tests for FODT → HTML export
3. Dogfood sample

### Option 3: Multi-sheet CSV and All-sheets HTML (DEPTH)
- FodsCsvExporter.ExportAllSheetsToCsv already exists
- FodsHtmlExporter could export multi-sheet

### Recommendation
Priority 1: RCA Proof Wiring sprint (wire proof graph to existing implementations)
Priority 2: FODT HTML Export sprint
Priority 3: Multi-sheet depth

## Policy Note
- CSV DOES unblock FODS → CSV (writer exists, exporter wired, tests pass)
- HTML DOES unblock FODS → HTML (writer exists, exporter wired, tests pass)
- TXT DOES unblock FODT → TXT (writer exists, exporter wired, tests pass)
- Markdown DOES unblock FODT → Markdown (writer exists, exporter wired, tests pass)
- But these do NOT imply support for formats NOT wired (e.g., FODT → HTML not yet implemented)
