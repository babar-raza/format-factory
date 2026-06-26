// Tests for FodsDocument.SetCellWrapping dedicated coverage.
// Sprint: ff-sprint-s277-dotnet-deepening-20260630
// Ledger: PC-FODS-R305

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R305: Dedicated tests for FodsDocument.SetCellWrapping(sheetName, row, col, wrap).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Set wrap=true no exception.
/// Set wrap=false no exception.
/// SheetCount unchanged after SetCellWrapping.
/// Set twice no exception.
/// Dogfood: set wrapping on multiple cells no exception.
/// </summary>
public class FodsR305SetCellWrappingDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellWrapping_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellWrapping(null!, 0, 0, true));
    }

    [Fact]
    public void SetCellWrapping_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellWrapping("   ", 0, 0, true));
    }

    [Fact]
    public void SetCellWrapping_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellWrapping("NoSuchSheet", 0, 0, true));
    }

    [Fact]
    public void SetCellWrapping_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellWrapping("Sheet1", -1, 0, true));
    }

    [Fact]
    public void SetCellWrapping_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellWrapping("Sheet1", 0, -1, true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellWrapping_WrapTrue_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellWrapping("Sheet1", 0, 0, true));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellWrapping_WrapFalse_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetCellWrapping("Sheet1", 0, 0, false));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellWrapping_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetCellWrapping("Sheet1", 0, 0, true);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellWrapping_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellWrapping("Sheet1", 0, 0, true);
        var ex = Record.Exception(() => doc.SetCellWrapping("Sheet1", 0, 0, false));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetWrappingOnMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex = Record.Exception(() =>
        {
            doc.SetCellWrapping("Data", 0, 0, true);
            doc.SetCellWrapping("Data", 0, 1, false);
            doc.SetCellWrapping("Data", 1, 0, true);
            doc.SetCellValue("Data", 0, 0, "Long text that wraps");
        });
        Assert.Null(ex);
    }
}
