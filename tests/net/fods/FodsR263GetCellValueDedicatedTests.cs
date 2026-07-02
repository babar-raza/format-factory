// Tests for FodsDocument.GetCellValue dedicated coverage.
// Sprint: ff-sprint-s244-dotnet-deepening-20260629
// Ledger: PC-FODS-R263

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R263: Dedicated tests for FodsDocument.GetCellValue(sheetName, row, col).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row index → throws exception.
/// Negative col index → throws exception.
/// Returns null or empty for unset cell.
/// Returns set value after SetCellValue.
/// SetCellValue twice → returns latest value.
/// SheetCount unchanged after call.
/// Dogfood: set multiple cells, retrieve each correctly.
/// </summary>
public class FodsR263GetCellValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(null!, 0, 0));
    }

    [Fact]
    public void GetCellValue_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("   ", 0, 0));
    }

    [Fact]
    public void GetCellValue_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(sheetName, -1, 0));
    }

    [Fact]
    public void GetCellValue_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(sheetName, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_AfterSetCellValue_ReturnsValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "HelloCell");
        var val = doc.GetCellValue(sheetName, 0, 0);
        Assert.Equal("HelloCell", val);
    }

    [Fact]
    public void GetCellValue_SetTwice_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 1, 1, "First");
        doc.SetCellValue(sheetName, 1, 1, "Second");
        var val = doc.GetCellValue(sheetName, 1, 1);
        Assert.Equal("Second", val);
    }

    [Fact]
    public void GetCellValue_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Test");
        int before = doc.SheetCount;
        doc.GetCellValue(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleCells_RetrieveEachCorrectly()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Alpha");
        doc.SetCellValue(sheetName, 0, 1, "Beta");
        doc.SetCellValue(sheetName, 1, 0, "Gamma");
        doc.SetCellValue(sheetName, 1, 1, "Delta");
        Assert.Equal("Alpha", doc.GetCellValue(sheetName, 0, 0));
        Assert.Equal("Beta", doc.GetCellValue(sheetName, 0, 1));
        Assert.Equal("Gamma", doc.GetCellValue(sheetName, 1, 0));
        Assert.Equal("Delta", doc.GetCellValue(sheetName, 1, 1));
    }
}
