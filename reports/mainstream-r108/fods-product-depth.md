# R108 FODS Product Depth

## New API: GetColumnCount
- `GetColumnCount(string sheetName)` — returns max cells in any row
- `GetColumnCount()` — default first sheet overload
- 8 tests in FodsR108GetColumnCountTests.cs
- 4 dogfood tests in FodsR108DogfoodSaveEditRoundtripTests.cs (save-after-edit roundtrip)
- Source diff: GetColumnCount added before GetCellCount
- Ledger entry: R108-GOVERNED-DOTNET-FODS-GETCOLUMNCOUNT-001
- SHA: a34fd878c41c9da244141d2aa25c6ea04360d6e8ac648244a8d7b2dce1a4723b
