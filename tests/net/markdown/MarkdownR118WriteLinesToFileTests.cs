// Tests for MarkdownWriter.WriteLinesToFile() — file-based Markdown output.
// Sprint: FORMAT-FACTORY-MARKDOWN-WRITER-R118-20260626
// Ledger: R118-GOVERNED-DOTNET-MARKDOWN-WRITELINESTFILE-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Markdown.Tests;

/// <summary>
/// R118: MarkdownWriter.WriteLinesToFile(lines, path) writes lines joined with LF
/// to a UTF-8 file (no BOM). Parent directories are created automatically.
/// Null lines become empty strings. Invalid paths throw MarkdownWriterException.
/// </summary>
public class MarkdownR118WriteLinesToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_md_r118_{Guid.NewGuid():N}.md");

    // ---- File existence ----

    [Fact]
    public void WriteLinesToFile_ValidArgs_CreatesFile()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new[] { "# Hello" }, path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Content correctness ----

    [Fact]
    public void WriteLinesToFile_SingleHeading_ContentPresentInFile()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new[] { "# Title" }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("# Title", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_MultipleLines_AllPresentInFile()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new[] { "## Section", "Body text.", "More body." }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("## Section", content);
            Assert.Contains("Body text.", content);
            Assert.Contains("More body.", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_NullLine_BecomeEmptyLineInFile()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new string?[] { "First", null, "Third" }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("First", content);
            Assert.Contains("Third", content);
            // The null line becomes an empty separator between content
            Assert.Contains("\n\n", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_EmptyList_CreatesFileWithEmptyContent()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new List<string?>(), path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.Equal(string.Empty, content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Encoding: UTF-8 no BOM, LF line endings ----

    [Fact]
    public void WriteLinesToFile_Encoding_NoUtf8Bom()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new[] { "# Heading", "Body" }, path);
            var bytes = File.ReadAllBytes(path);
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "File must not contain UTF-8 BOM");
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_LineEndings_UsesLfNotCrLf()
    {
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(new[] { "Line A", "Line B" }, path);
            var content = File.ReadAllText(path);
            Assert.DoesNotContain("\r\n", content);
            Assert.Contains("\n", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Error handling ----

    [Fact]
    public void WriteLinesToFile_NullPath_ThrowsMarkdownWriterException()
    {
        Assert.Throws<MarkdownWriterException>(() =>
            MarkdownWriter.WriteLinesToFile(new[] { "line" }, null!));
    }

    [Fact]
    public void WriteLinesToFile_EmptyPath_ThrowsMarkdownWriterException()
    {
        Assert.Throws<MarkdownWriterException>(() =>
            MarkdownWriter.WriteLinesToFile(new[] { "line" }, string.Empty));
    }

    // ---- Round-trip consistency ----

    [Fact]
    public void WriteLinesToFile_RoundTrip_ContentMatchesInMemoryWriteParagraphs()
    {
        var lines = new[] { "Introduction text.", "Second paragraph." };
        var path = TempPath();
        try
        {
            MarkdownWriter.WriteLinesToFile(lines, path);
            var fileContent = File.ReadAllText(path);
            var inMemoryContent = MarkdownWriter.WriteParagraphs(lines);
            // Both should produce the same normalized content
            Assert.Equal(inMemoryContent.Replace("\r\n", "\n"), fileContent.Replace("\r\n", "\n"));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Dogfood: FODT-style document pipeline ----

    [Fact]
    public void DogfoodPipeline_FodtStyleDocument_AllSectionsInFile()
    {
        var path = TempPath();
        try
        {
            var lines = new List<string?>
            {
                MarkdownWriter.WriteHeading("Document Title", 1),
                MarkdownWriter.WriteParagraphs(new[] { "Executive summary paragraph." }),
                MarkdownWriter.WriteHeading("Section One", 2),
                MarkdownWriter.WriteParagraphs(new[] { "Section one body text." }),
                MarkdownWriter.WriteHeading("Section Two", 2),
                MarkdownWriter.WriteParagraphs(new[] { "Section two body text." }),
                MarkdownWriter.WriteHeading("Conclusion", 3),
                MarkdownWriter.WriteParagraphs(new[] { "Concluding remarks." }),
            };

            MarkdownWriter.WriteLinesToFile(lines, path);
            var content = File.ReadAllText(path);

            // Structural markers
            Assert.Contains("# Document Title", content);
            Assert.Contains("## Section One", content);
            Assert.Contains("## Section Two", content);
            Assert.Contains("### Conclusion", content);

            // Body content
            Assert.Contains("Executive summary paragraph.", content);
            Assert.Contains("Section one body text.", content);
            Assert.Contains("Section two body text.", content);
            Assert.Contains("Concluding remarks.", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
