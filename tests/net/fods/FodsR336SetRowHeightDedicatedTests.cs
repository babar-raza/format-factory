// Tests for FodsDocument.SetRowHeight dedicated coverage.
// Sprint: ff-sprint-s308-dotnet-deepening-20260630
// Ledger: PC-FODS-R336

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R336: Dedicated tests for FodsDocument.SetRowHeight(sheetName, rowIndex, height).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row index throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetRowHeight.
/// Called twice no exception.
/// Multiple rows no exception.
/// Dogfood: set height on multiple sheets.
/// </summary>
public class FodsR336SetRowHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowHeight_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight(null!, 0, 25));
    }

    [Fact]
    public void SetRowHeight_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight("   ", 0, 25));
    }

    [Fact]
    public void SetRowHeight_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight("NoSuchSheet", 0, 25));
    }

    [Fact]
    public void SetRowHeight_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight("Sheet1", -1, 25));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowHeight_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetRowHeight("Sheet1", 0, 30));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetRowHeight("Sheet1", 0, 30);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetRowHeight_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetRowHeight("Sheet1", 0, 30);
        var ex = Record.Exception(() => doc.SetRowHeight("Sheet1", 0, 40));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_MultipleRows_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetRowHeight("Sheet1", 0, 25);
        var ex = Record.Exception(() => doc.SetRowHeight("Sheet1", 1, 35));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetHeightOnMultipleSheets_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Headers");
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        doc.SetRowHeight("Headers", 0, 40);
        doc.SetRowHeight("Data", 0, 20);
        doc.SetRowHeight("Data", 1, 20);
        Assert.Equal(before, doc.SheetCount);
    }
}
