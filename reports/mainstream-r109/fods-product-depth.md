# R109 FODS Product Depth Report

## New API: HasSheet(string name) → bool
- Checks whether a sheet with the given name exists
- Returns false for null/empty/whitespace (no exception thrown)
- O(1) lookup via existing GetSheetByName

## Source
- File: `src/net/fods/FodsDocument.cs`
- SHA before: `a34fd878c41c9da244141d2aa25c6ea04360d6e8ac648244a8d7b2dce1a4723b`
- SHA after: `8d2027865ef5876c0dbd7acf6b3de2b49a242c649058bd18aeec3e22d7072a30`

## Tests
- File: `tests/net/fods/FodsR109HasSheetTests.cs` (8 tests)
- Dogfood: `tests/net/fods/FodsR109DogfoodHasSheetRoundtripTests.cs` (4 tests)
- Total FODS .NET tests: 421

## Ledger
- Entry: R109-GOVERNED-DOTNET-FODS-HASSHEET-001
- Skill transcript: `reports/mainstream-r109/skill-transcripts/r109-fods-hassheet.md`
