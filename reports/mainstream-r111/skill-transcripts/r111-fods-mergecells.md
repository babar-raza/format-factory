# Skill Transcript: FODS MergeCells

- **Skill:** /add-dotnet-api
- **Sprint:** mainstream-r111
- **Format:** FODS
- **API:** MergeCells(sheetName, startRow, startCol, rowSpan, colSpan)
- **Behavior:** Merge rectangular range of cells. Sets table:number-columns-spanned/rows-spanned on anchor, replaces covered cells with covered-table-cell.
- **Source:** src/net/fods/FodsDocument.cs
- **Pre-SHA:** 606e5c19bbfab92037964a5ebd75b7bc8f790b83ac42780776814ff8387ed889
- **Post-SHA:** 0b4a2890c3ecb83006472500ff012556018bf26383493c8aa8165de72f0dcbd4
- **Tests:** tests/net/fods/FodsR111MergeCellsTests.cs (8 tests)
- **Ledger Entry:** R111-GOVERNED-DOTNET-FODS-MERGECELLS-001
- **Depth Class:** object_model_depth
