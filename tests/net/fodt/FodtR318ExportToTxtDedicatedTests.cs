// Tests for FodtDocument.ExportToTxt dedicated coverage.
// Sprint: ff-sprint-s303-dotnet-deepening-20260630
// Ledger: PC-FODT-R318

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R318: Dedicated tests for FodtDocument.ExportToTxt(filePath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid call no exception.
/// Output file exists after export.
/// Output file is non-empty.
/// ParagraphCount unchanged after ExportToTxt.
/// Export twice no exception.
/// Dogfood: document with paragraphs exports to txt.
/// Dogfood: export two different paths no exception.
/// </summary>
public class FodtR318ExportToTxtDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r318_{Guid.NewGuid():N}.txt");
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
    public void ExportToTxt_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.ExportToTxt(null!));
    }

    [Fact]
    public void ExportToTxt_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.ExportToTxt("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToTxt_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToTxt(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToTxt_OutputFileExists()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path = GetTempPath();
        doc.ExportToTxt(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToTxt_OutputFileNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path = GetTempPath();
        doc.ExportToTxt(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToTxt_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int before = doc.ParagraphCount;
        string path = GetTempPath();
        doc.ExportToTxt(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToTxt_ExportTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToTxt(path1);
        var ex = Record.Exception(() => doc.ExportToTxt(path2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_ExportsToTxt()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph.");
        doc.AddParagraph("Second paragraph.");
        doc.AddParagraph("Third paragraph.");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToTxt(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportTwoDifferentPaths_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document text content");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToTxt(path1);
        var ex = Record.Exception(() => doc.ExportToTxt(path2));
        Assert.Null(ex);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
