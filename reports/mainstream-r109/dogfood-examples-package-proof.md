# R109 Lane G: Dogfood, Examples, and Package/Install Proof

## Dogfood Tests Added

### FODS HasSheet Dogfood Roundtrip
- File: `tests/net/fods/FodsR109DogfoodHasSheetRoundtripTests.cs`
- Tests: 4
- Pipeline: HasSheet → GetColumnCount → InsertRowWithValues → Save → Reload → HasSheet
- Format Factory code path proven: uses FodsDocument.HasSheet, GetColumnCount, InsertRowWithValues, Save, Load

### FODT HTML Export Dogfood
- File: `tests/net/fodt/FodtR109DogfoodHtmlExportTests.cs`
- Tests: 4
- Pipeline: ExportToHtmlFile + ExportToMarkdownFile consistency, edit-save-export roundtrip
- Format Factory code path proven: uses FodtDocument.ExportToHtmlFile, ExportToMarkdownFile, AppendParagraph, Save, Load

## Package/Install Proof
- .NET: All 3 test projects build and pass (1165 total .NET tests)
  - FODS: 421 passed (dotnet test tests/net/fods/)
  - FODT: 409 passed (dotnet test tests/net/fodt/)
  - Netpbm: 335 passed (dotnet test tests/net/netpbm/)
- Python: All packages importable from .local/venv
  - ZST, SYLK, PBM, PGM, PPM, DIF, FODS, FODT all import successfully
  - 3104 Python tests pass from installed packages
- No new packages built in R109 (no Python source changes)

## Examples
- No new examples added in R109 (R107/R108 examples remain current)
- Existing examples cover: FODS CSV export, FODT plain text export, Netpbm equalize/convert, SYLK CSV pipeline

## Raw Logs
All test output captured in `reports/mainstream-r109/raw-logs/`:
- fods-dotnet-test.log, fodt-dotnet-test.log, netpbm-dotnet-test.log, python-all-test.log
