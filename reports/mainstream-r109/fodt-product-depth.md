# R109 FODT Product Depth Report

## New API: ExportToHtmlFile(string filePath) → void
- Writes HTML export to file on disk
- Complements ExportToHtml() (in-memory) and ExportToMarkdownFile (R108)
- Validates path not null/empty, throws ArgumentException
- Creates or overwrites target file

## Source
- File: `src/net/fodt/FodtDocument.cs`
- SHA before: `cbd0f6c40fa32d9ca4ddff7939c122c429a9d3075b8291cc6b667be761d6c9fb`
- SHA after: `f1517b171f5b6a3f5c69868ef0dd024dd207c6f365824512c8bdac62f176eba6`

## Tests
- File: `tests/net/fodt/FodtR109ExportToHtmlFileTests.cs` (8 tests)
- Dogfood: `tests/net/fodt/FodtR109DogfoodHtmlExportTests.cs` (4 tests)
- Total FODT .NET tests: 409

## Ledger
- Entry: R109-GOVERNED-DOTNET-FODT-EXPORTTOHTMLFILE-001
- Skill transcript: `reports/mainstream-r109/skill-transcripts/r109-fodt-exporttohtmlfile.md`
