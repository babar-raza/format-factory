// Tests for FodtDocument.ExportToHtml dedicated coverage.
// Sprint: ff-sprint-s302-dotnet-deepening-20260630
// Ledger: PC-FODT-R317

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R317: Dedicated tests for FodtDocument.ExportToHtml(filePath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid call no exception.
/// Output file exists after export.
/// Output file is non-empty.
/// ParagraphCount unchanged after ExportToHtml.
/// Export twice no exception.
/// Dogfood: document with paragraphs exports to html.
/// Dogfood: export two different paths no exception.
/// </summary>
public class FodtR317ExportToHtmlDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r317_{Guid.NewGuid():N}.html");
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
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml(null!));
    }

    [Fact]
    public void ExportToHtml_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToHtml(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToHtml_OutputFileExists()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtml_OutputFileNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToHtml_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int before = doc.ParagraphCount;
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToHtml_ExportTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToHtml(path1);
        var ex = Record.Exception(() => doc.ExportToHtml(path2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_ExportsToHtml()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddParagraph("Body text goes here.");
        doc.AddParagraph("Conclusion.");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToHtml(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportTwoDifferentPaths_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToHtml(path1);
        var ex = Record.Exception(() => doc.ExportToHtml(path2));
        Assert.Null(ex);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
