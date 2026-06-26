// Tests for FodtDocument.ExportToText dedicated coverage.
// Sprint: ff-sprint-s220-dotnet-deepening-20260629
// Ledger: PC-FODT-R235

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R235: Dedicated tests for FodtDocument.ExportToText(string path).
/// Null path → throws exception.
/// Empty doc: creates file.
/// File contains content.
/// Paragraph text appears in output.
/// Heading text appears in output.
/// ParagraphCount unchanged after export.
/// Export twice: file exists both times.
/// Multiple paragraphs all appear.
/// Dogfood: heading + paragraph pipeline.
/// Dogfood: set author then export — no exception.
/// </summary>
public class FodtR235ExportToTextDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".txt")
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_txt_test_{Guid.NewGuid():N}{suffix}");
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
    public void ExportToText_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.ExportToText(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToText_EmptyDoc_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath();
        doc.ExportToText(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToText_FileHasContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text content");
        var path = TempPath();
        doc.ExportToText(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Length > 0);
    }

    [Fact]
    public void ExportToText_ParagraphTextInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique text for export test");
        var path = TempPath();
        doc.ExportToText(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Unique text for export test", content);
    }

    [Fact]
    public void ExportToText_HeadingInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Text Export Heading", 1);
        var path = TempPath();
        doc.ExportToText(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Text Export Heading", content);
    }

    [Fact]
    public void ExportToText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        doc.AppendParagraph("Two");
        int before = doc.ParagraphCount;
        var path = TempPath();
        doc.ExportToText(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToText_ExportTwice_FileExistsBothTimes()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        var path = TempPath();
        doc.ExportToText(path);
        Assert.True(File.Exists(path));
        doc.ExportToText(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToText_MultipleParagraphs_AllInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para Alpha");
        doc.AppendParagraph("Para Beta");
        var path = TempPath();
        doc.ExportToText(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Para Alpha", content);
        Assert.Contains("Para Beta", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeadingAndParagraph_BothInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        doc.AppendParagraph("Chapter body text");
        var path = TempPath();
        doc.ExportToText(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Chapter One", content);
        Assert.Contains("Chapter body text", content);
    }

    [Fact]
    public void DogfoodPipeline_SetAuthorThenExport_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetAuthor("Export Author");
        doc.AppendParagraph("Authored content");
        var path = TempPath();
        var ex = Record.Exception(() => doc.ExportToText(path));
        Assert.Null(ex);
    }
}
