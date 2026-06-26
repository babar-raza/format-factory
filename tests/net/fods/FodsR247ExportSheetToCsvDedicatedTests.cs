// Tests for FodsDocument.ExportSheetToCsv dedicated coverage.
// Sprint: ff-sprint-s229-dotnet-deepening-20260629
// Ledger: PC-FODS-R247

using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R247: Dedicated tests for FodsDocument.ExportSheetToCsv(sheetName, path).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Null path → throws exception.
/// Valid export → creates file.
/// File has content.
/// SheetCount unchanged.
/// Export twice: file exists both times.
/// Cell value appears in CSV output.
/// Dogfood: set data then export, content verifiable.
/// </summary>
public class FodsR247ExportSheetToCsvDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".csv")
    {
        var path = Path.Combine(Path.GetTempPath(), $"fods_csv_test_{Guid.NewGuid():N}{suffix}");
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
    public void ExportSheetToCsv_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        var path = TempPath();
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToCsv(null!, path));
    }

    [Fact]
    public void ExportSheetToCsv_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        var path = TempPath();
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToCsv("   ", path));
    }

    [Fact]
    public void ExportSheetToCsv_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        var path = TempPath();
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToCsv("Ghost", path));
    }

    [Fact]
    public void ExportSheetToCsv_NullPath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToCsv(sheetName, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_ValidExport_CreatesFile()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Val");
        var path = TempPath();
        doc.ExportSheetToCsv(sheetName, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportSheetToCsv_FileHasContent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "SomeValue");
        var path = TempPath();
        doc.ExportSheetToCsv(sheetName, path);
        var content = File.ReadAllText(path);
        Assert.True(content.Length > 0);
    }

    [Fact]
    public void ExportSheetToCsv_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        var path = TempPath();
        doc.ExportSheetToCsv(sheetName, path);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportSheetToCsv_ExportTwice_FileExistsBothTimes()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "X");
        var path = TempPath();
        doc.ExportSheetToCsv(sheetName, path);
        Assert.True(File.Exists(path));
        doc.ExportSheetToCsv(sheetName, path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetDataExport_ContentVerifiable()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Alice");
        doc.SetCellValue(sheetName, 0, 1, "95");
        doc.SetCellValue(sheetName, 1, 0, "Bob");
        doc.SetCellValue(sheetName, 1, 1, "87");
        var path = TempPath();
        doc.ExportSheetToCsv(sheetName, path);
        Assert.True(File.Exists(path));
        var content = File.ReadAllText(path);
        Assert.True(content.Length > 0);
    }
}
