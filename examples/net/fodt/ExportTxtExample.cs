// FormatFactory.Fodt — FODT to Plain Text Export Example
//
// Demonstrates: Load a FODT document, export body text to a .txt file.
// Dogfood: FodtTxtExporter delegates serialization to FormatFactory.Txt.TxtWriter.
// This is a standalone example — not compiled as part of the test project.

using FormatFactory.Fodt;

// Export FODT document to a plain text file
var result = FodtTxtExporter.ExportTxt(
    fodtPath: "document.fodt",
    txtPath: "output/document.txt"
);
Console.WriteLine($"Exported: {result.ParagraphsExported} paragraphs → {result.OutputPath}");
Console.WriteLine($"Status: {result.Status}");

// Export using an already-loaded document
var doc = FodtDocument.Load("document.fodt");
var result2 = FodtTxtExporter.ExportTxt(doc, "document.fodt", "output/document2.txt");
Console.WriteLine($"Paragraphs exported: {result2.ParagraphsExported}");
