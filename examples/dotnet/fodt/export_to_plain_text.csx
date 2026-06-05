// FODT Plain Text Export Example — FormatFactory.Fodt
// Demonstrates: Load a FODT document, edit paragraphs, export to plain text file.

#r "../../../src/net/fodt/bin/Debug/net10.0/FormatFactory.Fodt.dll"
using FormatFactory.Fodt;

// 1. Load a minimal FODT document
var samplesDir = Path.GetFullPath(Path.Combine(
    AppContext.BaseDirectory, "../../../samples/by-format/fodt"));
var doc = FodtDocument.Load(Path.Combine(samplesDir, "minimal-document.fodt"));

// 2. Clear and rebuild content
doc.RemoveAllParagraphs();
doc.AppendParagraph("Meeting Notes — 2026-06-03");
doc.AppendParagraph("Attendees: Alice, Bob, Charlie");
doc.AppendParagraph("Action items:");
doc.AppendParagraph("  1. Review Q3 budget");
doc.AppendParagraph("  2. Finalize design spec");

// 3. Export to plain text file
var outputPath = Path.GetTempFileName() + ".txt";
doc.ExportToPlainTextFile(outputPath);
Console.WriteLine($"Plain text exported to: {outputPath}");
Console.WriteLine("--- Content ---");
Console.WriteLine(File.ReadAllText(outputPath));

// 4. Get heading texts (if any)
var headings = doc.GetHeadingTexts();
Console.WriteLine($"\nHeadings found: {headings.Count}");
foreach (var h in headings) Console.WriteLine($"  - {h}");

// Cleanup
File.Delete(outputPath);
