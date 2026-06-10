# Skill Transcript: /add-dotnet-api — FODS HasSheet

## Skill: add-dotnet-api
## Format: FODS
## API: HasSheet(string name) → bool
## Sprint: mainstream-r109
## Ledger Entry: R109-GOVERNED-DOTNET-FODS-HASSHEET-001

## Pre-Conditions
- Source SHA before: `a34fd878c41c9da244141d2aa25c6ea04360d6e8ac648244a8d7b2dce1a4723b`
- Ledger valid, latest_sprint: mainstream-r108

## Implementation
- Added `HasSheet(string name)` method to `FodsDocument.cs`
- Returns `false` for null/empty/whitespace, otherwise delegates to `GetSheetByName(name) != null`
- No new dependencies added

## Source SHA after: `8d2027865ef5876c0dbd7acf6b3de2b49a242c649058bd18aeec3e22d7072a30`

## Tests
- File: `tests/net/fods/FodsR109HasSheetTests.cs`
- Count: 8 tests
- All pass (421 total FODS tests)

## Validation
- Ledger entry added: R109-GOVERNED-DOTNET-FODS-HASSHEET-001
- Focused test: `dotnet test tests/net/fods/ --no-restore` — 421 passed, 0 failed
