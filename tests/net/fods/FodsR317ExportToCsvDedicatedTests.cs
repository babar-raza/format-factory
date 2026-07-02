// Tests for FodsDocument.ExportToCsv dedicated coverage.
// Sprint: ff-sprint-s289-dotnet-deepening-20260630
// Ledger: PC-FODS-R317

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R317: Dedicated tests for FodsDocument.ExportToCsv(sheetName, filePath).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Null file path throws exception.
/// Whitespace file path throws exception.
/// Valid call no exception.
/// File exists after ExportToCsv.
/// SheetCount unchanged after ExportToCsv.
/// Exported file is non-empty.
/// Dogfood: export sheet with data, file created.
/// </summary>
public class FodsR317ExportToCsvDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath(string suffix = ".csv")
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
    public void ExportToCsv_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv(null!, GetTempPath()));
    }

    [Fact]
    public void ExportToCsv_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv("   ", GetTempPath()));
    }

    [Fact]
    public void ExportToCsv_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv("NoSuchSheet", GetTempPath()));
    }

    [Fact]
    public void ExportToCsv_NullFilePath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv(sheet, null!));
    }

    [Fact]
    public void ExportToCsv_WhitespaceFilePath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv(sheet, "   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToCsv_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToCsv(sheet, path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToCsv_FileExistsAfterExport()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        string path = GetTempPath();
        doc.ExportToCsv(sheet, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToCsv_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.ExportToCsv(sheet, GetTempPath());
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportToCsv_ExportedFileNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "Data");
        string path = GetTempPath();
        doc.ExportToCsv(sheet, path);
        Assert.True(new FileInfo(path).Length > 0);
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
        doc.SetCellValue(sheet, 0, 0, "Name");
        doc.SetCellValue(sheet, 0, 1, "Score");
        doc.AddRow(sheet);
        doc.SetCellValue(sheet, 1, 0, "Alice");
        doc.SetCellValue(sheet, 1, 1, "95");
        string path = GetTempPath();
        doc.ExportToCsv(sheet, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }
}
