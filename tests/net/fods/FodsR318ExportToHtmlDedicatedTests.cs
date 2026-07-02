// Tests for FodsDocument.ExportToHtml dedicated coverage.
// Sprint: ff-sprint-s290-dotnet-deepening-20260630
// Ledger: PC-FODS-R318

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R318: Dedicated tests for FodsDocument.ExportToHtml(filePath).
/// Null file path throws exception.
/// Whitespace file path throws exception.
/// Valid call no exception.
/// File exists after ExportToHtml.
/// File is non-empty after ExportToHtml.
/// SheetCount unchanged after ExportToHtml.
/// Export twice no exception.
/// Dogfood: export sheet with data, file created.
/// Dogfood: export to different path, both files created.
/// </summary>
public class FodsR318ExportToHtmlDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath(string suffix = ".html")
    {
        string path = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString() + suffix);
        _tempFiles.Add(path);
        return path;
    }

    public void Dispose()
    {
        foreach (var f in _tempFiles)
            try { if (File.Exists(f)) File.Delete(f); } catch { }
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NullFilePath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml(null!));
    }

    [Fact]
    public void ExportToHtml_WhitespaceFilePath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToHtml("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToHtml(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToHtml_FileExistsAfterExport()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtml_FileNonEmptyAfterExport()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "Header");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToHtml_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.ExportToHtml(GetTempPath());
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportToHtml_ExportTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.ExportToHtml(GetTempPath());
        var ex = Record.Exception(() => doc.ExportToHtml(GetTempPath()));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ExportSheetWithData_FileCreated()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "Product");
        doc.SetCellValue(sheet, 0, 1, "Price");
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 1, 0, "Widget");
        doc.SetCellValue(sheet, 1, 1, "9.99");
        string path = GetTempPath();
        doc.ExportToHtml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportToDifferentPaths_BothCreated()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToHtml(path1);
        doc.ExportToHtml(path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
