// FormatFactory.Fods — FODS to CSV Export Example
//
// Demonstrates: Load a FODS spreadsheet, export sheets to CSV.
// This is a standalone example — not compiled as part of the test project.

using FormatFactory.Fods;

// 1. Export first sheet to a CSV file
var result = FodsCsvExporter.ExportFirstSheetToCsv(
    fodsPath: "spreadsheet.fods",
    csvPath: "output/sheet1.csv"
);
Console.WriteLine($"Exported: {result.SheetName} ({result.RowsExported} rows)");

// 2. Export ALL sheets to individual CSV files
var results = FodsCsvExporter.ExportAllSheetsToCsv(
    fodsPath: "spreadsheet.fods",
    outputDirPath: "output/all-sheets/"
);
foreach (var r in results)
    Console.WriteLine($"  {r.SheetName}: {r.RowsExported} rows → {r.OutputPath}");

// 3. In-memory export (no file I/O)
var doc = FodsDocument.Load("spreadsheet.fods");
var csvString = FodsCsvExporter.ExportSheetToCsvString(doc.Sheets[0]);
Console.WriteLine($"CSV length: {csvString.Length} chars");
