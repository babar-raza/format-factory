# Skill Transcript: FODS GetCellDataType

- **Skill:** /add-dotnet-api
- **Sprint:** mainstream-r110
- **Format:** FODS
- **API:** GetCellDataType(string sheetName, int row, int col) → string?
- **Behavior:** Returns the ODF office:value-type attribute of a cell. Returns null if not present or indices out of range.
- **Source:** src/net/fods/FodsDocument.cs
- **Pre-SHA:** 8d2027865ef5876c0dbd7acf6b3de2b49a242c649058bd18aeec3e22d7072a30
- **Post-SHA:** 606e5c19bbfab92037964a5ebd75b7bc8f790b83ac42780776814ff8387ed889
- **Tests:** tests/net/fods/FodsR110GetCellDataTypeTests.cs (8 tests)
- **Ledger Entry:** R110-GOVERNED-DOTNET-FODS-GETCELLDATATYPE-001
- **Depth Class:** helper
