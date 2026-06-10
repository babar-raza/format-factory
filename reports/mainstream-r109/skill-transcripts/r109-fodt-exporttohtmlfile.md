# Skill Transcript: /add-dotnet-api — FODT ExportToHtmlFile

## Skill: add-dotnet-api
## Format: FODT
## API: ExportToHtmlFile(string filePath) → void
## Sprint: mainstream-r109
## Ledger Entry: R109-GOVERNED-DOTNET-FODT-EXPORTTOHTMLFILE-001

## Pre-Conditions
- Source SHA before: `cbd0f6c40fa32d9ca4ddff7939c122c429a9d3075b8291cc6b667be761d6c9fb`
- Ledger valid, latest_sprint: mainstream-r108

## Implementation
- Added `ExportToHtmlFile(string filePath)` method to `FodtDocument.cs`
- Validates path not null/empty, delegates to `ExportToHtml()` + `File.WriteAllText`
- Follows same pattern as ExportToPlainTextFile and ExportToMarkdownFile

## Source SHA after: `f1517b171f5b6a3f5c69868ef0dd024dd207c6f365824512c8bdac62f176eba6`

## Tests
- File: `tests/net/fodt/FodtR109ExportToHtmlFileTests.cs`
- Count: 8 tests
- All pass (409 total FODT tests)

## Validation
- Ledger entry added: R109-GOVERNED-DOTNET-FODT-EXPORTTOHTMLFILE-001
- Focused test: `dotnet test tests/net/fodt/ --no-restore` — 409 passed, 0 failed
