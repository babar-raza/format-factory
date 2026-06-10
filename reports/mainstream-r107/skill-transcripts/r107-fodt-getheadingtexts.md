# Skill Transcript: FODT GetHeadingTexts

- **Skill:** /add-dotnet-api
- **Format:** FODT
- **API:** GetHeadingTexts() -> IReadOnlyList<string>
- **Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
- **Wave:** 2 (Commercial .NET APIs)

## Source File Changed
- `src/net/fodt/FodtDocument.cs` — Added GetHeadingTexts method

## Behavior
Returns text of heading-only elements (text:h) in the document, filtered from the Paragraphs collection which contains both paragraphs and headings.

## Tests Created
- `tests/net/fodt/FodtR107GetHeadingTextsTests.cs` — 8 tests
- `tests/net/fodt/FodtR107DogfoodPlainTextExportTests.cs` — shared dogfood coverage

## Validation
- `dotnet test tests/net/fodt/ --filter R107` — 22 passed, 0 failed
- Ledger record written to `reports/r90/product-code-change-ledger.json`
