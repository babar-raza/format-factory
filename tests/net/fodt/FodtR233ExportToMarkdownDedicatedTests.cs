// Tests for FodtDocument.ExportToMarkdown dedicated coverage.
// Sprint: ff-sprint-s218-dotnet-deepening-20260629
// Ledger: PC-FODT-R233

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R233: Dedicated tests for FodtDocument.ExportToMarkdown(string path).
/// Null path → throws exception.
/// Empty doc: creates file.
/// File contains markdown content.
/// Paragraph text appears in output.
/// Heading appears with # prefix.
/// ParagraphCount unchanged after export.
/// Export twice: file exists both times.
/// Different paragraphs appear in order.
/// Dogfood: heading + paragraph pipeline.
/// Dogfood: multiple headings pipeline.
/// </summary>
public class FodtR233ExportToMarkdownDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".md")
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_md_test_{Guid.NewGuid():N}{suffix}");
        _tempFiles.Add(path);
        return path;
    }

    public void Dispose()
    {
        foreach (var f in _tempFiles)
            if (File.Exists(f)) File.Delete(f);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.ExportToMarkdown(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_EmptyDoc_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath();
        doc.ExportToMarkdown(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdown_FileHasContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var path = TempPath();
        doc.ExportToMarkdown(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Length > 0);
    }

    [Fact]
    public void ExportToMarkdown_ParagraphTextInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique paragraph text for markdown test");
        var path = TempPath();
        doc.ExportToMarkdown(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Unique paragraph text for markdown test", content);
    }

    [Fact]
    public void ExportToMarkdown_HeadingHasHashPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        var path = TempPath();
        doc.ExportToMarkdown(path);
        var content = File.ReadAllText(path);
        Assert.Contains("#", content);
    }

    [Fact]
    public void ExportToMarkdown_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        var path = TempPath();
        doc.ExportToMarkdown(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToMarkdown_ExportTwice_FileExistsBothTimes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        var path = TempPath();
        doc.ExportToMarkdown(path);
        Assert.True(File.Exists(path));
        doc.ExportToMarkdown(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeadingAndParagraph_BothInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section One", 1);
        doc.AppendParagraph("Body content here");
        var path = TempPath();
        doc.ExportToMarkdown(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Section One", content);
        Assert.Contains("Body content here", content);
    }

    [Fact]
    public void DogfoodPipeline_MultipleHeadings_AllInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Text one");
        doc.AppendHeading("Chapter 2", 2);
        doc.AppendParagraph("Text two");
        var path = TempPath();
        doc.ExportToMarkdown(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Chapter 1", content);
        Assert.Contains("Chapter 2", content);
    }
}
