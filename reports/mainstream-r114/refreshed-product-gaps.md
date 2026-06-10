# Refreshed Product Gaps (TC-E-002)
Sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-DIRTY-STATE-COMMIT-AND-BREADTH-SPRINT-001
Generated: 2026-06-04

## Note: This document is READ-ONLY analysis. selected-product-gaps.json not modified.

Source: `.local/supervisor/selected-product-gaps.json` (R98 vintage — last updated before R94-R113 implementation)

---

## Gap Resolution Status

| Gap ID | Description | R98 Status | Current Status | Evidence |
|--------|-------------|-----------|----------------|---------|
| GAP-FODT-DOGFOOD-MD-DOTNET-001 | FODT → Markdown export | GAP_DOGFOOD_EXTERNAL | RESOLVED | FodtR112MarkdownExportDogfoodTests.cs |
| GAP-FODT-DOGFOOD-TXT-DOTNET-001 | FODT → TXT export | GAP_DOGFOOD_EXTERNAL | RESOLVED | FodtR113TxtDogfoodTests.cs |
| GAP-NETPBM-DOGFOOD-PIPELINE-DOTNET-001 | Netpbm Pipeline | NOT_PRESENT | RESOLVED (R114) | NetpbmR114FlipMergePipelineTests.cs |

---

## FODS Gaps

The breadth finalization sprint (2026-06-04) established FODS CSV as READY_FOR_MAINSTREAM.
From the R94–R113 test accumulation:
- ExportSheetToCsv: IMPLEMENTED (R107) — FodsR107ExportSheetToCsvTests.cs
- AddSheet, RemoveSheet, RenameSheet, CopySheet: IMPLEMENTED (R100-R104)
- GetRowValues, GetCellCount, GetRowCount, GetColumnCount: IMPLEMENTED (R96-R108)
- HasSheet, FindCellsByValue, GetCellDataType, GetUsedRange: IMPLEMENTED (R109-R112)
- MergeCells, SetCellFormula, SortRows, InsertRowWithValues: IMPLEMENTED (R107-R113)

## FODT Gaps

From the R94–R113 test accumulation:
- AppendParagraph, RemoveParagraph, InsertParagraph: IMPLEMENTED (R100-R102)
- GetWordCount, GetCharCount, GetHeadingCount, GetParagraphCount: IMPLEMENTED (R94-R97)
- ReplaceText roundtrip: IMPLEMENTED (R98)
- ExportToHtml, ExportToMarkdown, GetPlainText: IMPLEMENTED (R105-R107)
- InsertHeading, RemoveHeading, GetDocumentOutline: IMPLEMENTED (R110-R111)
- GetDocumentMetadata, GetDocumentStats: IMPLEMENTED (R104, R113)

## Netpbm Gaps

From the R94–R113 test accumulation + R114:
- Resize, ToGrayscale, GetBrightness, Clone: IMPLEMENTED (R94-R97)
- Rotate180/270/90: IMPLEMENTED (R100-R101)
- MergeHorizontal, MergeVertical: IMPLEMENTED (R104-R105)
- FlipDiagonal, Overlay, Crop: IMPLEMENTED (R106)
- Equalize, ConvertFormat, ApplyGamma: IMPLEMENTED (R107-R108)
- Sepia, Solarize, Posterize: IMPLEMENTED (R109-R110)
- Sharpen, BlurBox: IMPLEMENTED (R111)
- Tile: IMPLEMENTED (R113)
- **Pipeline: IMPLEMENTED (R114 — this sprint)**

---

## Action Required

A future "capability matrix update" sprint should:
1. Read poc-targets.yaml
2. Apply proposals from capability-matrix-proposals.md
3. Update selected-product-gaps.json to reflect current state
4. Get Supervisor and human approval
5. Commit the updates

This document is READ-ONLY. Do not modify poc-targets.yaml or selected-product-gaps.json
based on this analysis alone.
