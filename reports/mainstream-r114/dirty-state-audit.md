# Mainstream R114 — Dirty State Audit
Sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-DIRTY-STATE-COMMIT-AND-BREADTH-SPRINT-001
Generated: 2026-06-04 (TC-A-001)

## Summary

| Item | Count/Result |
|------|-------------|
| Uncommitted src/net/ insertions | +2477 lines |
| Uncommitted src/net/ files | 3 |
| Untracked tests/net/ files | 115 |
| Last committed source | R93 (3a86a05) |
| Python source changes | 1 (src/python/sylk/sylk_parser.py — minor) |

---

## Uncommitted src/net/ Changes

Source: `git diff --stat HEAD -- src/net/`

| File | Lines Added | Sprint Range |
|------|------------|-------------|
| src/net/fods/FodsDocument.cs | +868 | R94–R113 |
| src/net/fodt/FodtDocument.cs | +482 | R94–R113 |
| src/net/netpbm/Model/NetpbmImage.cs | +1127 | R94–R113 |
| **TOTAL** | **+2477** | |

These changes were accumulated across sprints R94–R113 but never committed (last commit was R93: `3a86a05`).

---

## Untracked Test Files (115 files)

### tests/net/fods/ — 39 files (R94–R113)
FodsR94ExportSheetToHtmlTests.cs, FodsR95ExportSheetToJsonTests.cs, FodsR96GetRowCountTests.cs,
FodsR97GetCellCountTests.cs, FodsR98SaveAfterEditTests.cs, FodsR99ExportQualityTests.cs,
FodsR100AddSheetTests.cs, FodsR101ExportSheetToMarkdownTests.cs, FodsR101RemoveSheetTests.cs,
FodsR102GetRowValuesTests.cs, FodsR103RenameSheetTests.cs, FodsR104CopySheetTests.cs,
FodsR104DogfoodCsvExportTests.cs, FodsR104GetSheetByIndexTests.cs, FodsR105DeleteRowsTests.cs,
FodsR105DogfoodRowOpsTests.cs, FodsR105InsertRowTests.cs, FodsR106ClearSheetTests.cs,
FodsR106DogfoodSaveRoundtripTests.cs, FodsR106GetColumnValuesTests.cs, FodsR107DogfoodCsvExportTests.cs,
FodsR107ExportSheetToCsvTests.cs, FodsR107InsertRowWithValuesTests.cs, FodsR108DogfoodSaveEditRoundtripTests.cs,
FodsR108GetColumnCountTests.cs, FodsR109DogfoodHasSheetRoundtripTests.cs, FodsR109HasSheetTests.cs,
FodsR110DogfoodCsvExportTests.cs, FodsR110FindCellsByValueTests.cs, FodsR110GetCellDataTypeTests.cs,
FodsR111DogfoodSaveRoundtripTests.cs, FodsR111MergeCellsTests.cs, FodsR111SetCellFormulaTests.cs,
FodsR112CsvExportDogfoodTests.cs, FodsR112GetUsedRangeTests.cs, FodsR112SaveRoundtripDepthTests.cs,
FodsR113InsertRowDepthTests.cs, FodsR113JsonDogfoodTests.cs, FodsR113SortRowsTests.cs

### tests/net/fodt/ — 40 files (R94–R113)
FodtR94GetWordCountTests.cs, FodtR95GetCharCountTests.cs, FodtR96GetHeadingCountTests.cs,
FodtR97GetParagraphCountTests.cs, FodtR98ReplaceTextRoundtripTests.cs, FodtR99ParagraphPersistenceTests.cs,
FodtR100AppendParagraphTests.cs, FodtR101InsertParagraphTests.cs, FodtR101RemoveParagraphTests.cs,
FodtR102InsertParagraphTests.cs, FodtR103GetPlainTextRangeTests.cs, FodtR104DogfoodExportTests.cs,
FodtR104GetDocumentStatsTests.cs, FodtR104SetParagraphTextTests.cs, FodtR105DogfoodHtmlExportTests.cs,
FodtR105ExportToHtmlTests.cs, FodtR105GetParagraphTextTests.cs, FodtR106DogfoodSaveRoundtripTests.cs,
FodtR106GetTextBetweenTests.cs, FodtR106RemoveAllParagraphsTests.cs, FodtR107DogfoodPlainTextExportTests.cs,
FodtR107ExportToPlainTextFileTests.cs, FodtR107GetHeadingTextsTests.cs, FodtR108DogfoodMarkdownExportTests.cs,
FodtR108ExportToMarkdownFileTests.cs, FodtR109DogfoodHtmlExportTests.cs, FodtR109ExportToHtmlFileTests.cs,
FodtR110DogfoodMarkdownExportTests.cs, FodtR110GetParagraphStyleNameTests.cs, FodtR110InsertHeadingTests.cs,
FodtR111DogfoodOutlineExportTests.cs, FodtR111GetDocumentOutlineTests.cs, FodtR111RemoveHeadingTests.cs,
FodtR112HeadingSaveRoundtripTests.cs, FodtR112MarkdownExportDogfoodTests.cs, FodtR112ReplaceTextSaveRoundtripTests.cs,
FodtR113ExportTxtDepthTests.cs, FodtR113GetDocumentMetadataTests.cs, FodtR113TxtDogfoodTests.cs

### tests/net/netpbm/ — 36 files (R94–R113)
NetpbmR94ResizeTests.cs, NetpbmR95ToGrayscaleTests.cs, NetpbmR96GetBrightnessTests.cs,
NetpbmR97CloneTests.cs, NetpbmR98SaveToFileTests.cs, NetpbmR99ToColorTests.cs,
NetpbmR100Rotate270Tests.cs, NetpbmR101GetHistogramTests.cs, NetpbmR101Rotate180Tests.cs,
NetpbmR102ThresholdTests.cs, NetpbmR103ExtractChannelTests.cs, NetpbmR104AdjustBrightnessTests.cs,
NetpbmR104DogfoodPipelineTests.cs, NetpbmR104MergeHorizontalTests.cs, NetpbmR105AdjustContrastTests.cs,
NetpbmR105DogfoodMergePipelineTests.cs, NetpbmR105MergeVerticalTests.cs, NetpbmR106DogfoodCropOverlayTests.cs,
NetpbmR106FlipDiagonalTests.cs, NetpbmR106OverlayTests.cs, NetpbmR107ConvertFormatTests.cs,
NetpbmR107DogfoodEqualizeOverlayTests.cs, NetpbmR107EqualizeTests.cs, NetpbmR108ApplyGammaTests.cs,
NetpbmR109PosterizeTests.cs, NetpbmR110DogfoodPosterizeSaveTests.cs, NetpbmR110SepiaTests.cs,
NetpbmR110SolarizeTests.cs, NetpbmR111BlurBoxTests.cs, NetpbmR111DogfoodSharpenSaveTests.cs,
NetpbmR111SharpenTests.cs, NetpbmR112ConvertFormatDogfoodTests.cs, NetpbmR112EqualizeDepthTests.cs,
NetpbmR112SepiaSaveRoundtripTests.cs, NetpbmR113CropSaveDepthTests.cs, NetpbmR113TileSaveDogfoodTests.cs,
NetpbmR113TileTests.cs

---

## Implementation Status (Key Capabilities)

### FODT Markdown Export
- Tests present: tests/net/fodt/FodtR112MarkdownExportDogfoodTests.cs (8 tests)
- Instance methods: doc.ExportToMarkdown() at FodtDocument.cs:522, doc.ExportToMarkdownFile() at :660
- Static class: FodtMarkdownExporter.ExportToMarkdown(string fodtPath, string mdPath) — file-to-file API
- Status: ALREADY_IMPLEMENTED (R112)

### FODT TXT Export
- Tests present: tests/net/fodt/FodtR113TxtDogfoodTests.cs (6 tests)
- Instance methods: doc.GetPlainText() at FodtDocument.cs:161, doc.ExportToPlainTextFile() at :647
- Static class: FodtTxtExporter.ExportTxt(string fodtPath, string txtPath) — file-to-file API
- Status: ALREADY_IMPLEMENTED (R113)

### FODS CSV Export
- Tests present: tests/net/fods/FodsR107ExportSheetToCsvTests.cs and FodsR107DogfoodCsvExportTests.cs
- Methods: FodsDocument.ExportSheetToCsv(string sheetName) at :821, ExportSheetToCsv() at :835
- Status: ALREADY_IMPLEMENTED (R107)

### Netpbm Pipeline Method
- No Pipeline() method in src/net/netpbm/Model/NetpbmImage.cs
- "pipeline" appears only in XML doc-comments as a descriptive word
- Status: NOT_IMPLEMENTED — this IS genuine new R114 work

---

## Implications for This Sprint

| Capability | Was Handoff Correct? | Action |
|-----------|---------------------|--------|
| FODT Markdown | WRONG signature (instance vs static mismatch) | Repair handoff to reflect actual API (instance methods on FodtDocument) |
| FODT TXT | WRONG method name (ExportToTxt vs ExportTxt) | Repair handoff; note capability already implemented |
| FODS CSV Dogfood | Already done at R107 | Lane D: CLOSED_SKIPPED_WITH_REASON |
| Netpbm Pipeline | Not implemented | Lane C: add Pipeline method (genuine R114 new work) |

---

## Note on Committed State

All R94–R113 src/net/ work is uncommitted. This sprint will stage that work for commit
(pending explicit user authorization). The build gate (TC-A-003) must pass before any
new implementation proceeds.
