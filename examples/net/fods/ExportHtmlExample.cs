// FormatFactory.Fods — FODS to HTML Export Example
//
// Demonstrates: Load a FODS spreadsheet, export all sheets to an HTML file.
// Dogfood: FodsHtmlExporter delegates HTML table serialization to FormatFactory.Html.HtmlWriter.
// This is a standalone example — not compiled as part of the test project.

using FormatFactory.Fods;

// Export FODS spreadsheet to an HTML file (all sheets as tables)
var result = FodsHtmlExporter.ExportToHtml(
    fodsPath: "spreadsheet.fods",
    htmlPath: "output/spreadsheet.html"
);
Console.WriteLine($"Exported: {result.SheetsExported} sheets ({result.TotalRowsExported} rows) → {result.OutputPath}");

// Export and inspect using an already-loaded document
var doc = FodsDocument.Load("spreadsheet.fods");
var result2 = FodsHtmlExporter.ExportToHtml(doc, "spreadsheet.fods", "output/spreadsheet2.html");
Console.WriteLine($"Sheets: {result2.SheetsExported}, Output: {result2.OutputPath}");
