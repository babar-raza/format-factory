// Example: FODS ClearSheet + GetColumnValues
// Demonstrates clearing a sheet and extracting column data.

using FormatFactory.Fods;

var doc = FodsDocument.Load("samples/by-format/fods/minimal-spreadsheet.fods");
var sheet = doc.GetSheetNames()[0];

Console.WriteLine($"Rows before clear: {doc.GetRowCount(sheet)}");

// Extract column 0 values before clearing
var col0 = doc.GetColumnValues(sheet, 0);
Console.WriteLine($"Column 0 values: {string.Join(", ", col0)}");

// Clear the sheet
doc.ClearSheet(sheet);
Console.WriteLine($"Rows after clear: {doc.GetRowCount(sheet)}");

// Rebuild with new data
for (int i = 0; i < 3; i++)
    doc.InsertRow(sheet, i);
Console.WriteLine($"Rows after rebuild: {doc.GetRowCount(sheet)}");
