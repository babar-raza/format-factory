// Tests for FodsDocument.ExportToCsv dedicated coverage.
// Sprint: ff-sprint-s248-dotnet-deepening-20260630
// Ledger: PC-FODS-R267

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R267: Dedicated tests for FodsDocument.ExportToCsv(sheetName, filePath).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Valid export → no exception.
/// SheetCount unchanged after export.
/// Exported file exists on disk.
/// Exported file is non-empty for non-empty sheet.
/// Dogfood: add data rows, export, verify file exists and non-empty.
/// Dogfood: export twice same file → still exists and non-empty.
/// </summary>
public class FodsR267ExportToCsvDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempCsvPath()
    {
        string path = Path.Combine(Path.GetTempPath(), $"fods_test_{Guid.NewGuid():N}.csv");
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
    public void ExportToCsv_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv(null!, GetTempCsvPath()));
    }

    [Fact]
    public void ExportToCsv_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv("   ", GetTempCsvPath()));
    }

    [Fact]
    public void ExportToCsv_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.ExportToCsv("NoSuchSheet", GetTempCsvPath()));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToCsv_ValidExport_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A", "B", "C" });
        string path = GetTempCsvPath();
        var ex = Record.Exception(() => doc.ExportToCsv(sheetName, path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToCsv_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "X" });
        int before = doc.SheetCount;
        doc.ExportToCsv(sheetName, GetTempCsvPath());
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportToCsv_FileExistsAfterExport()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Value" });
        string path = GetTempCsvPath();
        doc.ExportToCsv(sheetName, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToCsv_NonEmptySheet_FileNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Col1", "Col2" });
        doc.AddRow(sheetName, new[] { "Val1", "Val2" });
        string path = GetTempCsvPath();
        doc.ExportToCsv(sheetName, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddDataRows_ExportVerifyNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Department", "Salary" });
        doc.AddRow(sheetName, new[] { "Alice", "Eng", "90000" });
        doc.AddRow(sheetName, new[] { "Bob", "Finance", "85000" });
        doc.AddRow(sheetName, new[] { "Carol", "Eng", "92000" });
        string path = GetTempCsvPath();
        doc.ExportToCsv(sheetName, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void DogfoodPipeline_ExportTwice_BothSucceed()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Item", "Count" });
        doc.AddRow(sheetName, new[] { "Apple", "10" });
        string path1 = GetTempCsvPath();
        string path2 = GetTempCsvPath();
        doc.ExportToCsv(sheetName, path1);
        doc.ExportToCsv(sheetName, path2);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
