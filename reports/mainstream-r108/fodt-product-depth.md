# R108 FODT Product Depth

## New API: ExportToMarkdownFile
- `ExportToMarkdownFile(string filePath)` — writes ExportToMarkdown() to file
- 8 tests in FodtR108ExportToMarkdownFileTests.cs
- 4 dogfood tests in FodtR108DogfoodMarkdownExportTests.cs (save+markdown roundtrip)
- Source diff: ExportToMarkdownFile added after ExportToPlainTextFile
- Ledger entry: R108-GOVERNED-DOTNET-FODT-EXPORTTOMARKDOWNFILE-001
- SHA: cbd0f6c40fa32d9ca4ddff7939c122c429a9d3075b8291cc6b667be761d6c9fb
