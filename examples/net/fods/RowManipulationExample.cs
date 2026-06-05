// Example: FODS Row Manipulation — InsertRow + DeleteRows
// Demonstrates adding and removing rows from a FODS spreadsheet.

using FormatFactory.Fods;

// Load a FODS file
var doc = FodsDocument.Load("samples/by-format/fods/minimal-spreadsheet.fods");
var sheet = doc.GetSheetNames()[0];

Console.WriteLine($"Sheet: {sheet}");
Console.WriteLine($"Rows before: {doc.GetRowCount(sheet)}");

// Insert a new row at position 0
doc.InsertRow(sheet, 0);
Console.WriteLine($"Rows after insert: {doc.GetRowCount(sheet)}");

// Delete 1 row starting at position 0
doc.DeleteRows(sheet, 0, 1);
Console.WriteLine($"Rows after delete: {doc.GetRowCount(sheet)}");

// Export to HTML for verification
var html = doc.ExportSheetToHtml(sheet);
Console.WriteLine($"HTML length: {html.Length} chars");
