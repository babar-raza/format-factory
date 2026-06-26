// Tests for FodsDocument.ExportToJson dedicated coverage.
// Sprint: ff-sprint-s291-dotnet-deepening-20260630
// Ledger: PC-FODS-R319

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R319: Dedicated tests for FodsDocument.ExportToJson(filePath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid call no exception.
/// Output file exists after export.
/// Output file is non-empty.
/// SheetCount unchanged after ExportToJson.
/// Export twice no exception.
/// Dogfood: document with data exports to json.
/// Dogfood: export two different paths no exception.
/// </summary>
public class FodsR319ExportToJsonDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"fods_r319_{Guid.NewGuid():N}.json");
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
    public void ExportToJson_NullPath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToJson(null!));
    }

    [Fact]
    public void ExportToJson_WhitespacePath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToJson("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToJson(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToJson_OutputFileExists()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        doc.ExportToJson(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToJson_OutputFileNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        doc.ExportToJson(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToJson_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string path = GetTempPath();
        doc.ExportToJson(path);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportToJson_ExportTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToJson(path1);
        var ex = Record.Exception(() => doc.ExportToJson(path2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithData_ExportsToJson()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Product");
        doc.SetCellValue("Data", 0, 1, "Price");
        doc.SetCellValue("Data", 1, 0, "Widget");
        doc.SetCellValue("Data", 1, 1, "9.99");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToJson(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportTwoDifferentPaths_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Value");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToJson(path1);
        var ex = Record.Exception(() => doc.ExportToJson(path2));
        Assert.Null(ex);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
