// Tests for FodsDocument.ExportToJson dedicated coverage.
// Sprint: ff-sprint-s264-dotnet-deepening-20260630
// Ledger: PC-FODS-R288

using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R288: Dedicated tests for FodsDocument.ExportToJson(sheetName, filePath).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Valid export → no exception.
/// Output file exists after export.
/// Output file is non-empty for sheets with data.
/// SheetCount unchanged after export.
/// Dogfood: export data sheet, file exists.
/// Dogfood: export two sheets to separate paths, both exist.
/// </summary>
public class FodsR288ExportToJsonDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string name)
    {
        string path = Path.Combine(Path.GetTempPath(), $"FodsR288_{name}_{Guid.NewGuid():N}.json");
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
    public void ExportToJson_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string path = TempPath("null");
        Assert.ThrowsAny<Exception>(() => doc.ExportToJson(null!, path));
    }

    [Fact]
    public void ExportToJson_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string path = TempPath("ws");
        Assert.ThrowsAny<Exception>(() => doc.ExportToJson("   ", path));
    }

    [Fact]
    public void ExportToJson_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string path = TempPath("nosheet");
        Assert.ThrowsAny<Exception>(() => doc.ExportToJson("DoesNotExist", path));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_ValidSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string path = TempPath("valid");
        var ex = Record.Exception(() => doc.ExportToJson("Sheet1", path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToJson_OutputFileExists()
    {
        var doc = FodsDocument.CreateNew();
        string path = TempPath("exists");
        doc.ExportToJson("Sheet1", path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToJson_DataSheet_NonEmptyFile()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "name", "score" });
        doc.AddRow("Data", new[] { "Alice", "95" });
        string path = TempPath("data");
        doc.ExportToJson("Data", path);
        long size = new FileInfo(path).Length;
        Assert.True(size > 0);
    }

    [Fact]
    public void ExportToJson_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string path = TempPath("count");
        doc.ExportToJson("Sheet1", path);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ExportDataSheet_FileExists()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Inventory");
        doc.AddRow("Inventory", new[] { "item", "qty", "price" });
        doc.AddRow("Inventory", new[] { "widget", "100", "9.99" });
        string path = TempPath("inventory");
        doc.ExportToJson("Inventory", path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheetsTwoFiles_BothExist()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        string pathA = TempPath("alpha");
        string pathB = TempPath("beta");
        doc.ExportToJson("Alpha", pathA);
        doc.ExportToJson("Beta", pathB);
        Assert.True(File.Exists(pathA));
        Assert.True(File.Exists(pathB));
    }
}
