// Example: FODT HTML Export — ExportToHtml + GetParagraphText
// Demonstrates exporting a FODT document to HTML and reading paragraph text.

using FormatFactory.Fodt;

// Load a FODT file
var doc = FodtDocument.Load("samples/by-format/fodt/minimal-document.fodt");

Console.WriteLine($"Paragraphs: {doc.ParagraphCount}");

// Read individual paragraph text
for (int i = 0; i < Math.Min(doc.ParagraphCount, 5); i++)
{
    var text = doc.GetParagraphText(i);
    Console.WriteLine($"  [{i}] {text}");
}

// Export full document to HTML
var html = doc.ExportToHtml();
Console.WriteLine($"\nHTML output ({html.Length} chars):");
Console.WriteLine(html[..Math.Min(html.Length, 500)]);
