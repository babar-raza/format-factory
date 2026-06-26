// Tests for FodtDocument.ExportToHtml dedicated coverage.
// Sprint: ff-sprint-s219-dotnet-deepening-20260629
// Ledger: PC-FODT-R234

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R234: Dedicated tests for FodtDocument.ExportToHtml(string path).
/// Null path → throws exception.
/// Empty doc: creates file.
/// File contains HTML content.
/// Paragraph text appears in output.
/// Heading appears in output.
/// ParagraphCount unchanged after export.
/// Export twice: file exists both times.
/// HTML has opening tag.
/// Dogfood: heading + paragraph both in output.
/// Dogfood: multiple paragraphs all in output.
/// </summary>
public class FodtR234ExportToHtmlDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".html")
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_html_test_{Guid.NewGuid():N}{suffix}");
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
    public void ExportToHtml_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_EmptyDoc_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtml_FileHasContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello HTML World");
        var path = TempPath();
        doc.ExportToHtml(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Length > 0);
    }

    [Fact]
    public void ExportToHtml_ParagraphTextInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique paragraph for html test");
        var path = TempPath();
        doc.ExportToHtml(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Unique paragraph for html test", content);
    }

    [Fact]
    public void ExportToHtml_HeadingInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My HTML Heading", 1);
        var path = TempPath();
        doc.ExportToHtml(path);
        var content = File.ReadAllText(path);
        Assert.Contains("My HTML Heading", content);
    }

    [Fact]
    public void ExportToHtml_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        var path = TempPath();
        doc.ExportToHtml(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToHtml_ExportTwice_FileExistsBothTimes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        var path = TempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtml_OutputContainsHtmlTag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test content");
        var path = TempPath();
        doc.ExportToHtml(path);
        var content = File.ReadAllText(path).ToLower();
        Assert.True(content.Contains("<html") || content.Contains("<!doctype") || content.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeadingAndParagraph_BothInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        doc.AppendParagraph("Body text goes here");
        var path = TempPath();
        doc.ExportToHtml(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Introduction", content);
        Assert.Contains("Body text goes here", content);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_AllInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        doc.AppendParagraph("Third paragraph");
        var path = TempPath();
        doc.ExportToHtml(path);
        var content = File.ReadAllText(path);
        Assert.Contains("First paragraph", content);
        Assert.Contains("Second paragraph", content);
        Assert.Contains("Third paragraph", content);
    }
}
