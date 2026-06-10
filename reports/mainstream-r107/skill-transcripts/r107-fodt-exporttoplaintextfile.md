# Skill Transcript: FODT ExportToPlainTextFile

- **Skill:** /add-dotnet-api
- **Format:** FODT
- **API:** ExportToPlainTextFile(string filePath)
- **Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
- **Wave:** 2 (Commercial .NET APIs)

## Source File Changed
- `src/net/fodt/FodtDocument.cs` — Added ExportToPlainTextFile method

## Behavior
Writes GetPlainText() output to the specified file path via File.WriteAllText. Creates/overwrites the file.

## Tests Created
- `tests/net/fodt/FodtR107ExportToPlainTextFileTests.cs` — 8 tests
- `tests/net/fodt/FodtR107DogfoodPlainTextExportTests.cs` — 6 dogfood tests

## Validation
- `dotnet test tests/net/fodt/ --filter R107` — 22 passed, 0 failed
- Ledger record written to `reports/r90/product-code-change-ledger.json`
