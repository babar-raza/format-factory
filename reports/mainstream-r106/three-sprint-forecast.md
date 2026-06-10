# Three-Sprint Forecast: R107 / R108 / R109

## R107 — POC Completion Push
- FODS: RemoveSheet, RenameSheet, GetCellCount (complete sheet management)
- FODT: ReplaceText, GetHeadingTexts, InsertParagraphAt (content manipulation)
- Netpbm: Threshold, AdjustGamma, SaveToFile overloads (image processing depth)
- FOSS: DIF write capability, SYLK hardening, PBM/PGM binary roundtrip
- Dogfood: 3+ new pipeline tests using RemoveSheet/ReplaceText/Threshold
- Target: 4000+ total tests

## R108 — Dogfood and Integration Depth
- FODS: MergeSheets, ExportWorkbookToJson (multi-sheet operations)
- FODT: Table of Contents extraction, style-aware paragraph ops
- Netpbm: Multi-image montage, format conversion (PGM<->PPM)
- FOSS: Full DIF roundtrip, FODS Python write capability
- Integration: Cross-format dogfood pipelines (FODS->HTML->validate)
- Target: 4200+ total tests

## R109 — Pre-Publication Hardening
- Edge case hardening across all .NET APIs (fuzz-like boundary tests)
- Performance benchmarks for large files (1000+ rows/paragraphs/pixels)
- Documentation completeness audit (all APIs have examples)
- Package matrix verification (all wheels build clean)
- Gate 11 preparation: commercial readiness evidence compilation
- Target: 4400+ total tests
