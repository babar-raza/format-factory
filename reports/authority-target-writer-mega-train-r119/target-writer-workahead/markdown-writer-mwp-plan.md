# Markdown Writer MWP Plan
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Status: ALREADY IMPLEMENTED

`FormatFactory.Markdown` is fully implemented and wired to FODT Markdown export.

| Check | Status |
|-------|--------|
| Library exists | `src/net/markdown/MarkdownWriter.cs` ✓ |
| Project file | `src/net/markdown/FormatFactory.Markdown.csproj` ✓ |
| Tests | `tests/net/markdown/MarkdownWriterTests.cs` — 11/11 PASS ✓ |
| Wired to FODT | `FodtMarkdownExporter.cs` uses MarkdownWriter ✓ |
| FODT tests pass | 520/520 PASS ✓ |

## Export Policy Compliance
- [x] Standalone writer library exists
- [x] FODT exporter delegates to writer
- [x] Tests prove delegation
- [ ] Dogfood sample to be produced in next sprint
- [ ] Registry entry proposed (not yet applied)
- [ ] RCA proof graph linked (RCA R2 sprint)

## Next Sprint Work Items
- Add `FormatFactory.Markdown` to registry via proposed patch
- Wire RCA proof graph: claim:fodt:export_markdown → MarkdownWriter node → tests → dogfood
- Produce dogfood sample: FODT → Markdown output artifact
- Note: Markdown does NOT unblock FODS → Markdown (different product)
