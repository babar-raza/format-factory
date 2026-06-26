// Tests for FodtDocument.ExportToPdf dedicated coverage.
// Sprint: ff-sprint-s272-dotnet-deepening-20260630
// Ledger: PC-FODT-R287

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R287: Dedicated tests for FodtDocument.ExportToPdf(outputPath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid path no exception.
/// File exists after export.
/// Non-empty content → non-empty file.
/// ParagraphCount unchanged after export.
/// TableCount unchanged after export.
/// Dogfood: document with paragraphs — pdf file exists.
/// Dogfood: export twice to different paths — both exist.
/// </summary>
public class FodtR287ExportToPdfDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath(string suffix = ".pdf")
    {
        var path = Path.Combine(Path.GetTempPath(), $"FodtR287_{Guid.NewGuid():N}{suffix}");
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
    public void ExportToPdf_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.ExportToPdf(null!));
    }

    [Fact]
    public void ExportToPdf_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.ExportToPdf("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_ValidPath_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Test content");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToPdf(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToPdf_FileExistsAfterExport()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("PDF export test");
        string path = GetTempPath();
        doc.ExportToPdf(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToPdf_NonEmptyContent_ProducesNonEmptyFile()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content for PDF");
        string path = GetTempPath();
        doc.ExportToPdf(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToPdf_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int before = doc.ParagraphCount;
        doc.ExportToPdf(GetTempPath());
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToPdf_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int tablesBefore = doc.TableCount;
        doc.ExportToPdf(GetTempPath());
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_PdfFileExists()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section 1");
        doc.AddParagraph("The body of section one.");
        doc.AddParagraph("Section 2");
        string path = GetTempPath();
        doc.ExportToPdf(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportTwiceToDifferentPaths_BothExist()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToPdf(path1);
        doc.ExportToPdf(path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
