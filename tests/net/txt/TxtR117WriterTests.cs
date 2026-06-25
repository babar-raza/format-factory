// Tests for TxtWriter static API: WriteLines, WriteParagraphs, WriteLinesToFile.
// Sprint: FORMAT-FACTORY-TXT-WRITER-R117-20260626
// Ledger: R117-GOVERNED-DOTNET-TXT-WRITER-001

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Txt.Tests;

/// <summary>
/// R117: TxtWriter static API — WriteLines(IEnumerable{string?}) produces plain text
/// with one entry per line. WriteParagraphs(IEnumerable{string?}) produces paragraphs
/// separated by blank lines. WriteLinesToFile(lines, path) persists to disk.
/// All methods handle null values gracefully.
/// </summary>
public class TxtR117WriterTests
{
    // ---- WriteLines: basic output ----

    [Fact]
    public void WriteLines_SingleLine_ContentPresent()
    {
        var output = TxtWriter.WriteLines(new[] { "Hello plain text" });
        Assert.Contains("Hello plain text", output);
    }

    [Fact]
    public void WriteLines_MultipleLines_AllPresent()
    {
        var output = TxtWriter.WriteLines(new[] { "Line A", "Line B", "Line C" });
        Assert.Contains("Line A", output);
        Assert.Contains("Line B", output);
        Assert.Contains("Line C", output);
    }

    [Fact]
    public void WriteLines_MultipleLines_HasNewlines()
    {
        var output = TxtWriter.WriteLines(new[] { "First", "Second" });
        Assert.Contains("\n", output);
    }

    [Fact]
    public void WriteLines_EmptyList_DoesNotThrow()
    {
        var output = TxtWriter.WriteLines(Array.Empty<string>());
        Assert.NotNull(output);
    }

    [Fact]
    public void WriteLines_NullEntriesHandled()
    {
        // Null entries should not throw
        var output = TxtWriter.WriteLines(new string?[] { "A", null, "B" });
        Assert.Contains("A", output);
        Assert.Contains("B", output);
    }

    // ---- WriteParagraphs ----

    [Fact]
    public void WriteParagraphs_SingleParagraph_ContentPresent()
    {
        var output = TxtWriter.WriteParagraphs(new[] { "This is a paragraph." });
        Assert.Contains("This is a paragraph.", output);
    }

    [Fact]
    public void WriteParagraphs_MultipleParagraphs_AllContentPresent()
    {
        var output = TxtWriter.WriteParagraphs(new[] { "Paragraph one.", "Paragraph two." });
        Assert.Contains("Paragraph one.", output);
        Assert.Contains("Paragraph two.", output);
    }

    [Fact]
    public void WriteParagraphs_MultipleParagraphs_SeparatedByNewlines()
    {
        var output = TxtWriter.WriteParagraphs(new[] { "First", "Second" });
        Assert.Contains("\n", output);
    }

    // ---- WriteLinesToFile ----

    [Fact]
    public void WriteLinesToFile_FileCreatedWithContent()
    {
        var path = Path.GetTempFileName();
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "File line one", "File line two" }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("File line one", content);
            Assert.Contains("File line two", content);
        }
        finally
        {
            File.Delete(path);
        }
    }

    [Fact]
    public void WriteLinesToFile_EmptyList_CreatesEmptyOrMinimalFile()
    {
        var path = Path.GetTempFileName();
        try
        {
            TxtWriter.WriteLinesToFile(Array.Empty<string>(), path);
            // Should not throw; file may be empty or have just a newline
            Assert.True(File.Exists(path));
        }
        finally
        {
            File.Delete(path);
        }
    }

    // ---- Dogfood: WriteLines → WriteLinesToFile → reload ----

    [Fact]
    public void DogfoodPipeline_WriteLinesAndFile_ContentIntact()
    {
        var lines = new[] { "Format Factory", "TXT Writer", "R117 Dogfood Test" };

        // In-memory
        var inMemory = TxtWriter.WriteLines(lines);
        Assert.Contains("Format Factory", inMemory);
        Assert.Contains("R117 Dogfood Test", inMemory);

        // To file and back
        var path = Path.GetTempFileName();
        try
        {
            TxtWriter.WriteLinesToFile(lines, path);
            var fromFile = File.ReadAllText(path);
            Assert.Contains("Format Factory", fromFile);
            Assert.Contains("TXT Writer", fromFile);
        }
        finally
        {
            File.Delete(path);
        }
    }
}
