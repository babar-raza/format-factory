# Skill Transcript: FODS ExportSheetToCsv

- **Skill:** /add-dotnet-api
- **Format:** FODS
- **API:** ExportSheetToCsv(string sheetName) + 2 overloads
- **Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
- **Wave:** 2 (Commercial .NET APIs)

## Source File Changed
- `src/net/fods/FodsDocument.cs` — Added ExportSheetToCsv method with RFC 4180 CSV formatting

## Behavior
Exports a named sheet as CSV text. Commas within values are quoted, double-quotes are doubled. Overloads: default first sheet, named sheet, sheet-name with separator.

## Tests Created
- `tests/net/fods/FodsR107ExportSheetToCsvTests.cs` — 8 tests
- `tests/net/fods/FodsR107DogfoodCsvExportTests.cs` — 6 dogfood tests

## Validation
- `dotnet test tests/net/fods/ --filter R107` — 22 passed, 0 failed
- Ledger record written to `reports/r90/product-code-change-ledger.json`
