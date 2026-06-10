# Skill Transcript: FODS InsertRowWithValues

- **Skill:** /add-dotnet-api
- **Format:** FODS
- **API:** InsertRowWithValues(string sheetName, int rowIndex, IReadOnlyList<string?> values)
- **Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
- **Wave:** 2 (Commercial .NET APIs)

## Source File Changed
- `src/net/fods/FodsDocument.cs` — Added InsertRowWithValues method

## Behavior
Creates a table-row with table-cell elements containing text:p for each value. Null values produce empty cells (no text:p child). Inserts at specified row index within the named sheet.

## Tests Created
- `tests/net/fods/FodsR107InsertRowWithValuesTests.cs` — 8 tests
- `tests/net/fods/FodsR107DogfoodCsvExportTests.cs` — shared dogfood coverage

## Validation
- `dotnet test tests/net/fods/ --filter R107` — 22 passed, 0 failed
- Ledger record written to `reports/r90/product-code-change-ledger.json`
