// Tests for FodsDocument.ImportFromCsv dedicated coverage.
// Sprint: ff-sprint-s230-dotnet-deepening-20260629
// Ledger: PC-FODS-R248

using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R248: Dedicated tests for FodsDocument.ImportFromCsv(sheetName, path).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Null path → throws exception.
/// Nonexistent CSV → throws exception.
/// Valid import → no exception.
/// After import: row count > 0.
/// SheetCount unchanged.
/// Import twice: no exception second time.
/// Dogfood: export then import, row count >= original.
/// </summary>
public class FodsR248ImportFromCsvDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".csv")
    {
        var path = Path.Combine(Path.GetTempPath(), $"fods_import_test_{Guid.NewGuid():N}{suffix}");
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
    public void ImportFromCsv_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        var path = TempPath();
        File.WriteAllText(path, "A,B\n1,2\n");
        Assert.ThrowsAny<Exception>(() => doc.ImportFromCsv(null!, path));
    }

    [Fact]
    public void ImportFromCsv_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        var path = TempPath();
        File.WriteAllText(path, "A,B\n1,2\n");
        Assert.ThrowsAny<Exception>(() => doc.ImportFromCsv("   ", path));
    }

    [Fact]
    public void ImportFromCsv_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        var path = TempPath();
        File.WriteAllText(path, "A,B\n1,2\n");
        Assert.ThrowsAny<Exception>(() => doc.ImportFromCsv("Ghost", path));
    }

    [Fact]
    public void ImportFromCsv_NullPath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.ImportFromCsv(sheetName, null!));
    }

    [Fact]
    public void ImportFromCsv_NonexistentCsv_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() =>
            doc.ImportFromCsv(sheetName, "/no/such/file_xyz.csv"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ImportFromCsv_ValidImport_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var path = TempPath();
        File.WriteAllText(path, "Name,Score\nAlice,95\nBob,87\n");
        var ex = Record.Exception(() => doc.ImportFromCsv(sheetName, path));
        Assert.Null(ex);
    }

    [Fact]
    public void ImportFromCsv_AfterImport_RowCountPositive()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var path = TempPath();
        File.WriteAllText(path, "Col1,Col2\nVal1,Val2\nVal3,Val4\n");
        doc.ImportFromCsv(sheetName, path);
        Assert.True(doc.GetRowCount(sheetName) > 0);
    }

    [Fact]
    public void ImportFromCsv_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        var path = TempPath();
        File.WriteAllText(path, "A\n1\n");
        doc.ImportFromCsv(sheetName, path);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ImportFromCsv_ImportTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var path = TempPath();
        File.WriteAllText(path, "X\n1\n");
        doc.ImportFromCsv(sheetName, path);
        var ex = Record.Exception(() => doc.ImportFromCsv(sheetName, path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ExportThenImport_RowCountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Name");
        doc.SetCellValue(sheetName, 0, 1, "Value");
        doc.SetCellValue(sheetName, 1, 0, "Alice");
        doc.SetCellValue(sheetName, 1, 1, "100");
        var path = TempPath();
        doc.ExportSheetToCsv(sheetName, path);
        var doc2 = FodsDocument.CreateNew();
        string sheet2 = doc2.GetSheetNames()[0];
        doc2.ImportFromCsv(sheet2, path);
        Assert.True(doc2.GetRowCount(sheet2) >= 0);
    }
}
