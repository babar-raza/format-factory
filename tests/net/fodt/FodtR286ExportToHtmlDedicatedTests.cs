// Tests for FodtDocument.ExportToHtml dedicated coverage.
// Sprint: ff-sprint-s271-dotnet-deepening-20260630
// Ledger: PC-FODT-R286

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R286: Dedicated tests for FodtDocument.ExportToHtml(outputPath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid path no exception.
/// File exists after export.
/// Non-empty content → non-empty file.
/// ParagraphCount unchanged after export.
/// TableCount unchanged after export.
/// Dogfood: document with paragraphs — html file exists and non-empty.
/// Dogfood: export twice both succeed.
/// </summary>
public class FodtR286ExportToHtmlDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath(string suffix = ".html")
    {
        var path = Path.Combine(Path.GetTempPath(), $"FodtR286_{Guid.NewGuid():N}{suffix}");
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
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml(null!));
    }

    [Fact]
    public void ExportToHtml_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_ValidPath_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Test paragraph");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToHtml(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToHtml_FileExistsAfterExport()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("HTML export test");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtml_NonEmptyContent_ProducesNonEmptyFile()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content for HTML");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToHtml_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int before = doc.ParagraphCount;
        doc.ExportToHtml(GetTempPath());
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToHtml_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int tablesBefore = doc.TableCount;
        doc.ExportToHtml(GetTempPath());
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_HtmlFileExistsAndNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Title");
        doc.AddParagraph("Body paragraph one.");
        doc.AddParagraph("Body paragraph two.");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void DogfoodPipeline_ExportTwiceToDifferentPaths_BothExist()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToHtml(path1);
        doc.ExportToHtml(path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
