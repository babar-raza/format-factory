# Proposed Capability Matrix Updates
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Status: PROPOSED — Not Applied

## Summary of Writer Readiness vs. Current Matrix

| Writer | Library | Exporter Wired | Tests | Current Matrix Status | Proposed Status |
|--------|---------|----------------|-------|----------------------|-----------------|
| FormatFactory.Csv | ✓ Built | FodsCsvExporter ✓ | 15+547 | BLOCKED | MWP_IMPLEMENTED |
| FormatFactory.Html | ✓ Built | FodsHtmlExporter ✓ | 12+547 | BLOCKED | MWP_IMPLEMENTED |
| FormatFactory.Txt | ✓ Built | FodtTxtExporter ✓ | 8+520 | BLOCKED | MWP_IMPLEMENTED |
| FormatFactory.Markdown | ✓ Built | FodtMarkdownExporter ✓ | 11+520 | BLOCKED | MWP_IMPLEMENTED |

## Constraints
- All proposed status changes require Gate 11 commercial readiness approval (Babar Raza)
- No capability matrix mutation occurs this sprint
- Proposed changes are tracked in `capability-delta-proposal.yaml`

## Not Unblocked by This Sprint
- FODT → HTML (no FodtHtmlExporter.cs)
- Any cross-product wiring (e.g., FODS using Markdown writer)
