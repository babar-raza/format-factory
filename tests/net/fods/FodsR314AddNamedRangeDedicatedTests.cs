// Tests for FodsDocument.AddNamedRange dedicated coverage.
// Sprint: ff-sprint-s286-dotnet-deepening-20260630
// Ledger: PC-FODS-R314

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R314: Dedicated tests for FodsDocument.AddNamedRange(name, sheetName, startRow, startCol, endRow, endCol).
/// Null name throws exception.
/// Whitespace name throws exception.
/// Null sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative start row throws exception.
/// Valid call no exception.
/// SheetCount unchanged after AddNamedRange.
/// Called twice no exception.
/// Dogfood: add named range on default sheet.
/// Dogfood: add multiple named ranges no exception.
/// </summary>
public class FodsR314AddNamedRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNamedRange_NullName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.AddNamedRange(null!, sheet, 0, 0, 1, 1));
    }

    [Fact]
    public void AddNamedRange_WhitespaceName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.AddNamedRange("   ", sheet, 0, 0, 1, 1));
    }

    [Fact]
    public void AddNamedRange_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddNamedRange("Range1", null!, 0, 0, 1, 1));
    }

    [Fact]
    public void AddNamedRange_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.AddNamedRange("Range1", "NoSuchSheet", 0, 0, 1, 1));
    }

    [Fact]
    public void AddNamedRange_NegativeStartRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.AddNamedRange("Range1", sheet, -1, 0, 1, 1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNamedRange_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() => doc.AddNamedRange("SalesRange", sheet, 0, 0, 5, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.AddNamedRange("MyRange", sheet, 0, 0, 2, 2);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void AddNamedRange_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddNamedRange("Range1", sheet, 0, 0, 1, 1);
        var ex = Record.Exception(() => doc.AddNamedRange("Range2", sheet, 2, 0, 3, 1));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddNamedRangeOnDefaultSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() => doc.AddNamedRange("DataRange", sheet, 1, 0, 10, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_AddMultipleNamedRanges_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() =>
        {
            doc.AddNamedRange("Headers", sheet, 0, 0, 0, 5);
            doc.AddNamedRange("Data", sheet, 1, 0, 20, 5);
            doc.AddNamedRange("Totals", sheet, 21, 0, 21, 5);
        });
        Assert.Null(ex);
    }
}
