// Tests for FodsDocument.FreezePanes dedicated coverage.
// Sprint: ff-sprint-s275-dotnet-deepening-20260630
// Ledger: PC-FODS-R303

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R303: Dedicated tests for FodsDocument.FreezePanes(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after FreezePanes.
/// Call twice no exception.
/// Dogfood: freeze rows and cols no exception.
/// Dogfood: freeze then add data, no exception.
/// </summary>
public class FodsR303FreezePanesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FreezePanes_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.FreezePanes(null!, 1, 1));
    }

    [Fact]
    public void FreezePanes_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.FreezePanes("   ", 1, 1));
    }

    [Fact]
    public void FreezePanes_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.FreezePanes("NoSuchSheet", 1, 1));
    }

    [Fact]
    public void FreezePanes_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.FreezePanes("Sheet1", -1, 1));
    }

    [Fact]
    public void FreezePanes_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.FreezePanes("Sheet1", 1, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FreezePanes_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.FreezePanes("Sheet1", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void FreezePanes_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.FreezePanes("Sheet1", 1, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void FreezePanes_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.FreezePanes("Sheet1", 1, 1);
        var ex = Record.Exception(() => doc.FreezePanes("Sheet1", 2, 2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FreezeRowsAndCols_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() =>
        {
            doc.FreezePanes("Data", 1, 0); // freeze header row
            // re-freeze with both row and col
            doc.FreezePanes("Data", 1, 1);
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_FreezeThenAddData_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        var ex = Record.Exception(() =>
        {
            doc.FreezePanes("Report", 1, 0);
            doc.SetCellValue("Report", 0, 0, "Header");
            doc.SetCellValue("Report", 1, 0, "Data1");
        });
        Assert.Null(ex);
    }
}
