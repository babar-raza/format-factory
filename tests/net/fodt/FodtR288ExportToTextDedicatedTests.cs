// Tests for FodtDocument.ExportToText dedicated coverage.
// Sprint: ff-sprint-s273-dotnet-deepening-20260630
// Ledger: PC-FODT-R288

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R288: Dedicated tests for FodtDocument.ExportToText(outputPath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid path no exception.
/// File exists after export.
/// Non-empty content → non-empty file.
/// ParagraphCount unchanged after export.
/// TableCount unchanged after export.
/// Dogfood: document with paragraphs — text file exists and non-empty.
/// Dogfood: export twice to different paths — both exist.
/// </summary>
public class FodtR288ExportToTextDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath(string suffix = ".txt")
    {
        var path = Path.Combine(Path.GetTempPath(), $"FodtR288_{Guid.NewGuid():N}{suffix}");
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
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.ExportToText(null!));
    }

    [Fact]
    public void ExportToText_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.ExportToText("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToText_ValidPath_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Export test");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToText(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToText_FileExistsAfterExport()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text export test");
        string path = GetTempPath();
        doc.ExportToText(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToText_NonEmptyContent_ProducesNonEmptyFile()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content for text export");
        string path = GetTempPath();
        doc.ExportToText(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int before = doc.ParagraphCount;
        doc.ExportToText(GetTempPath());
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int tablesBefore = doc.TableCount;
        doc.ExportToText(GetTempPath());
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_TextFileExistsAndNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddParagraph("This is the body of the document.");
        doc.AddParagraph("Conclusion");
        string path = GetTempPath();
        doc.ExportToText(path);
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
        doc.ExportToText(path1);
        doc.ExportToText(path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
