# HTML Writer MWP Plan
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Status: ALREADY IMPLEMENTED

`FormatFactory.Html` is fully implemented and wired to FODS HTML export.

| Check | Status |
|-------|--------|
| Library exists | `src/net/html/HtmlWriter.cs` ✓ |
| Project file | `src/net/html/FormatFactory.Html.csproj` ✓ |
| Tests | `tests/net/html/HtmlWriterTests.cs` — 12/12 PASS ✓ |
| Wired to FODS | `FodsHtmlExporter.cs` uses HtmlWriter ✓ |
| FODS tests pass | 547/547 PASS ✓ |

## Not Yet Implemented
- FODT → HTML export (no FodtHtmlExporter.cs exists)
  - This is a NEW capability, not a repair
  - Requires a new sprint with dedicated FODT HTML exporter implementation

## Next Sprint Work Items
- Add `FormatFactory.Html` to registry via proposed patch
- Wire RCA proof graph: claim:fods:export_html → HtmlWriter node → tests → dogfood
- Produce dogfood sample: FODS → HTML output artifact
- New sprint: FodtHtmlExporter.cs using HtmlWriter for FODT → HTML support
