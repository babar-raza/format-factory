// Example: Get document statistics from a FODT file
// Requires: FormatFactory.Fodt NuGet package (commercial .NET track)
//
// Usage:
//   var doc = FodtDocument.Load("document.fodt");
//   var (words, chars, paras, headings) = doc.GetDocumentStats();

using System;
using FormatFactory.Fodt;

// Load a FODT document
var doc = FodtDocument.Load("samples/by-format/fodt/minimal-document.fodt");

// Get all stats in one call
var (words, chars, paras, headings) = doc.GetDocumentStats();
Console.WriteLine("Document Statistics:");
Console.WriteLine($"  Words:      {words}");
Console.WriteLine($"  Characters: {chars}");
Console.WriteLine($"  Paragraphs: {paras}");
Console.WriteLine($"  Headings:   {headings}");

// Edit a paragraph
doc.SetParagraphText(0, "Updated first paragraph with new content");
Console.WriteLine($"\nAfter editing paragraph 0:");

var statsAfter = doc.GetDocumentStats();
Console.WriteLine($"  Words:      {statsAfter.WordCount}");
Console.WriteLine($"  Paragraphs: {statsAfter.ParagraphCount}");

// Add content and re-check
doc.AppendParagraph("A brand new paragraph");
var statsFinal = doc.GetDocumentStats();
Console.WriteLine($"\nAfter appending paragraph:");
Console.WriteLine($"  Paragraphs: {statsFinal.ParagraphCount}");

// Export to plaintext
var text = doc.GetPlainText();
Console.WriteLine($"\nPlain text preview: {text[..Math.Min(80, text.Length)]}...");
