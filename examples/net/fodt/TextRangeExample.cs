// Example: FODT RemoveAllParagraphs + GetTextBetweenParagraphs
// Demonstrates clearing and rebuilding a document, then extracting text ranges.

using FormatFactory.Fodt;

var doc = FodtDocument.Load("samples/by-format/fodt/minimal-document.fodt");

Console.WriteLine($"Original paragraphs: {doc.ParagraphCount}");

// Clear all content
doc.RemoveAllParagraphs();
Console.WriteLine($"After clear: {doc.ParagraphCount}");

// Rebuild with new content
doc.AppendParagraph("Introduction");
doc.AppendParagraph("Body text goes here.");
doc.AppendParagraph("More body text.");
doc.AppendParagraph("Conclusion");

// Extract a range
var range = doc.GetTextBetweenParagraphs(1, 3);
Console.WriteLine($"\nParagraphs 1-2:\n{range}");

// Export to HTML
var html = doc.ExportToHtml();
Console.WriteLine($"\nHTML length: {html.Length} chars");
