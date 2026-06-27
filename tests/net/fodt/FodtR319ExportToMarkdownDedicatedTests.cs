// Tests for FodtDocument.ExportToMarkdown dedicated coverage.
// Sprint: ff-sprint-s304-dotnet-deepening-20260630
// Ledger: PC-FODT-R319

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R319: Dedicated tests for FodtDocument.ExportToMarkdown(filePath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid call no exception.
/// Output file exists after export.
/// Output file is non-empty.
/// ParagraphCount unchanged after ExportToMarkdown.
/// Export twice no exception.
/// Dogfood: document with paragraphs exports to markdown.
/// Dogfood: export two different paths no exception.
/// </summary>
public class FodtR319ExportToMarkdownDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r319_{Guid.NewGuid():N}.md");
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
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        Assert.ThrowsAny<Exception>(() => doc.ExportToMarkdown(null!));
    }

    [Fact]
    public void ExportToMarkdown_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        Assert.ThrowsAny<Exception>(() => doc.ExportToMarkdown("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToMarkdown(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToMarkdown_OutputFileExists()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        string path = GetTempPath();
        doc.ExportToMarkdown(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToMarkdown_OutputFileNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        string path = GetTempPath();
        doc.ExportToMarkdown(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToMarkdown_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int before = doc.ParagraphCount;
        string path = GetTempPath();
        doc.ExportToMarkdown(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToMarkdown_ExportTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToMarkdown(path1);
        var ex = Record.Exception(() => doc.ExportToMarkdown(path2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_ExportsToMarkdown()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddParagraph("This is the body text.");
        doc.AddParagraph("Conclusion");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToMarkdown(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportTwoDifferentPaths_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section One");
        doc.AddParagraph("Section Two");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToMarkdown(path1);
        var ex = Record.Exception(() => doc.ExportToMarkdown(path2));
        Assert.Null(ex);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
