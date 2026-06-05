// FormatFactory.Fodt — FODT to Markdown Export Example
//
// Demonstrates: Load a FODT document, export headings and paragraphs to a Markdown file.
// Dogfood: FodtMarkdownExporter delegates heading formatting and file output to
//          FormatFactory.Markdown.MarkdownWriter.
// This is a standalone example — not compiled as part of the test project.

using FormatFactory.Fodt;

// Export FODT document to a Markdown file
var result = FodtMarkdownExporter.ExportToMarkdown(
    fodtPath: "document.fodt",
    mdPath: "output/document.md"
);
Console.WriteLine($"Exported: {result.ParagraphsExported} paragraphs → {result.OutputPath}");
Console.WriteLine($"Status: {result.Status}");

// Export using an already-loaded document
var doc = FodtDocument.Load("document.fodt");
var result2 = FodtMarkdownExporter.ExportToMarkdown(doc, "document.fodt", "output/document2.md");
Console.WriteLine($"Paragraphs exported: {result2.ParagraphsExported}");
