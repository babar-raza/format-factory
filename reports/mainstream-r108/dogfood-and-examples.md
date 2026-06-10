# R108 Dogfood and Examples

## Dogfood Tests

### FODS Save-After-Edit Roundtrip (4 tests)
- FodsR108DogfoodSaveEditRoundtripTests.cs
- Proves: Load->Edit->Save->Reload->Verify cycle
- Tests: cell edit roundtrip, clear+insert+csv, column count preserved, full pipeline

### FODT Markdown Export Roundtrip (4 tests)
- FodtR108DogfoodMarkdownExportTests.cs
- Proves: Load->Edit->Save->Reload->ExportToMarkdownFile cycle
- Tests: edit+save+markdown, clear+rebuild, markdown+plaintext consistency, replace+save+markdown
