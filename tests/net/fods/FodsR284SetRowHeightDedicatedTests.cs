// Tests for FodsDocument.SetRowHeight dedicated coverage.
// Sprint: ff-sprint-s261-dotnet-deepening-20260630
// Ledger: PC-FODS-R284

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R284: Dedicated tests for FodsDocument.SetRowHeight(sheetName, rowIndex, height).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative row index → throws exception.
/// Valid call → no exception.
/// SheetCount unchanged after call.
/// Set same row twice → no exception.
/// GetRowHeight returns a positive value after set.
/// Dogfood: set row height on populated sheet.
/// Dogfood: set multiple row heights, each no-exception.
/// </summary>
public class FodsR284SetRowHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowHeight_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight(null!, 0, 30));
    }

    [Fact]
    public void SetRowHeight_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight("   ", 0, 30));
    }

    [Fact]
    public void SetRowHeight_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight("NoSheet", 0, 30));
    }

    [Fact]
    public void SetRowHeight_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetRowHeight("Sheet1", -1, 30));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetRowHeight_ValidArgs_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetRowHeight("Sheet1", 0, 40));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetRowHeight("Sheet1", 0, 25);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetRowHeight_SetSameRowTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetRowHeight("Sheet1", 0, 20);
        var ex = Record.Exception(() => doc.SetRowHeight("Sheet1", 0, 50));
        Assert.Null(ex);
    }

    [Fact]
    public void SetRowHeight_GetRowHeight_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetRowHeight("Sheet1", 0, 35);
        double height = doc.GetRowHeight("Sheet1", 0);
        Assert.True(height > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PopulatedSheet_SetRowHeightNoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddRow("Data", new[] { "col1", "col2" });
        doc.AddRow("Data", new[] { "val1", "val2" });
        var ex = Record.Exception(() => doc.SetRowHeight("Data", 0, 45));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetMultipleRowHeights_AllNoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex0 = Record.Exception(() => doc.SetRowHeight("Sheet1", 0, 20));
        var ex1 = Record.Exception(() => doc.SetRowHeight("Sheet1", 1, 30));
        var ex2 = Record.Exception(() => doc.SetRowHeight("Sheet1", 2, 40));
        Assert.Null(ex0);
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
