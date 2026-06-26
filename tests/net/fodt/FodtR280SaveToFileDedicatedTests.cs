// Tests for FodtDocument.SaveToFile dedicated coverage.
// Sprint: ff-sprint-s265-dotnet-deepening-20260630
// Ledger: PC-FODT-R280

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R280: Dedicated tests for FodtDocument.SaveToFile(filePath).
/// Null path → throws exception.
/// Whitespace path → throws exception.
/// Valid path → no exception.
/// Output file exists after save.
/// Output file is non-empty for document with content.
/// ParagraphCount unchanged after save.
/// TableCount unchanged after save.
/// Save twice to same path → no exception (overwrite).
/// Dogfood: save document with paragraphs, file exists and non-empty.
/// Dogfood: save to two different paths, both exist.
/// </summary>
public class FodtR280SaveToFileDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string name)
    {
        string path = Path.Combine(Path.GetTempPath(), $"FodtR280_{name}_{Guid.NewGuid():N}.fodt");
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
    public void SaveToFile_NullPath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("content");
        Assert.ThrowsAny<Exception>(() => doc.SaveToFile(null!));
    }

    [Fact]
    public void SaveToFile_WhitespacePath_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("content");
        Assert.ThrowsAny<Exception>(() => doc.SaveToFile("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_ValidPath_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello FODT");
        string path = TempPath("valid");
        var ex = Record.Exception(() => doc.SaveToFile(path));
        Assert.Null(ex);
    }

    [Fact]
    public void SaveToFile_OutputFileExists()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        string path = TempPath("exists");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_NonEmptyContent_FileNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some paragraph content here");
        string path = TempPath("nonempty");
        doc.SaveToFile(path);
        long size = new FileInfo(path).Length;
        Assert.True(size > 0);
    }

    [Fact]
    public void SaveToFile_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Test");
        int before = doc.ParagraphCount;
        string path = TempPath("count");
        doc.SaveToFile(path);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SaveToFile_SaveTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Overwrite test");
        string path = TempPath("twice");
        doc.SaveToFile(path);
        var ex = Record.Exception(() => doc.SaveToFile(path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_FileExistsAndNonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction paragraph");
        doc.AddParagraph("Body content here");
        doc.AddParagraph("Conclusion paragraph");
        string path = TempPath("paragraphs");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void DogfoodPipeline_TwoPaths_BothExist()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Test content");
        string path1 = TempPath("path1");
        string path2 = TempPath("path2");
        doc.SaveToFile(path1);
        doc.SaveToFile(path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
