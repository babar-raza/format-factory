# R88 Train H: FODS .NET Product Deepening

## Train: H (Group 3 — Commercial .NET)
## Sprint: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## Work Done

### ExportAllSheetsToCsv API
Added `FodsCsvExporter.ExportAllSheetsToCsv()` to `src/net/fods/FodsCsvExporter.cs`:
- Exports ALL sheets from a FODS document to individual CSV files
- Sheet names sanitized for filesystem safety
- Duplicate sheet name handling with numeric suffix
- Returns `List<FodsCsvExportResult>` with per-sheet status

### Tests Added
File: `tests/net/fods/FodsR88MultiSheetCsvTests.cs` (8 tests)
- ExportAllSheets_MultiSheet_CreatesMultipleFiles
- ExportAllSheets_MultiSheet_UsesSheetNamesAsFilenames
- ExportAllSheets_MinimalSingleSheet_ReturnsOneResult
- ExportAllSheets_CreatesOutputDirectory
- ExportAllSheets_NullPath_Throws
- ExportAllSheets_NullOutputDir_Throws
- ExportAllSheets_EachResultHasSourcePath
- ExportAllSheets_SheetNamesPopulated

## Test Result
FODS .NET: 185 passed, 0 failed (was 177 baseline, +8 new)

## Status: COMPLETE
