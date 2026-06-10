# R109 Dogfood and Examples

## FODS Dogfood — HasSheet + GetColumnCount Pipeline
- File: `tests/net/fods/FodsR109DogfoodHasSheetRoundtripTests.cs`
- Tests: 4 (HasSheet→GetColumnCount pipeline, add→has→insert→save, guard before export, full lifecycle)
- Demonstrates: defensive HasSheet check before operations, multi-API roundtrip

## FODT Dogfood — HTML + Markdown Export Consistency
- File: `tests/net/fodt/FodtR109DogfoodHtmlExportTests.cs`
- Tests: 4 (both files create, edit→save→exportHtml, HTML+Markdown same content, replace→export)
- Demonstrates: dual-export workflow, edit-save-export pipeline
