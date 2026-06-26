// Tests for FodsDocument.SetColumnWidth dedicated coverage.
// Sprint: ff-sprint-s236-dotnet-deepening-20260629
// Ledger: PC-FODS-R254

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R254: Dedicated tests for FodsDocument.SetColumnWidth(sheetName, colIndex, width).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative column index → throws exception.
/// Valid call → no exception.
/// SheetCount unchanged after call.
/// Multiple columns — no exception.
/// Set and SaveToFile works without error.
/// Called twice → no exception.
/// Dogfood: set multiple column widths, file saves successfully.
/// </summary>
public class FodsR254SetColumnWidthDedicatedTests : IDisposable
{
    private readonly System.Collections.Generic.List<string> _tempFiles = new();

    private string TempPath(string suffix = ".fods")
    {
        var path = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            $"fods_cw_test_{System.Guid.NewGuid():N}{suffix}");
        _tempFiles.Add(path);
        return path;
    }

    public void Dispose()
    {
        foreach (var f in _tempFiles)
            if (System.IO.File.Exists(f)) System.IO.File.Delete(f);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth(null!, 0, 100));
    }

    [Fact]
    public void SetColumnWidth_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("   ", 0, 100));
    }

    [Fact]
    public void SetColumnWidth_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("NoSuchSheet", 0, 100));
    }

    [Fact]
    public void SetColumnWidth_NegativeColIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth(sheetName, -1, 100));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SetColumnWidth(sheetName, 0, 150));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.SetColumnWidth(sheetName, 0, 120);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetColumnWidth_MultipleColumns_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetColumnWidth(sheetName, 0, 100);
        doc.SetColumnWidth(sheetName, 1, 200);
        var ex = Record.Exception(() => doc.SetColumnWidth(sheetName, 2, 150));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetColumnWidth(sheetName, 0, 100);
        var ex = Record.Exception(() => doc.SetColumnWidth(sheetName, 0, 200));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleWidths_SaveToFileSucceeds()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Age", "City" });
        doc.SetColumnWidth(sheetName, 0, 150);
        doc.SetColumnWidth(sheetName, 1, 80);
        doc.SetColumnWidth(sheetName, 2, 200);
        var path = TempPath();
        var ex = Record.Exception(() => doc.SaveToFile(path));
        Assert.Null(ex);
        Assert.True(System.IO.File.Exists(path));
    }
}
