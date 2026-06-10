# Skill Transcript: FODS GetColumnValues

- **Skill:** /add-dotnet-api
- **Format:** FODS
- **API:** GetColumnValues(string sheetName, int col)
- **Sprint:** mainstream-r106
- **Source:** src/net/fods/FodsDocument.cs
- **Tests:** tests/net/fods/FodsR106GetColumnValuesTests.cs (8 tests, all pass)
- **Ledger entry:** reports/r90/product-code-change-ledger.json (R106-FODS-GETCOLUMNVALUES)
- **Behavior:** Returns IReadOnlyList<string?> of text values at the given column index across all rows. Returns null for cells beyond column count.
- **SHA-256:** efdce289780691819aaf2e9e22d3c2aca2c1982f300fcd746cd59d4d05c890bd
