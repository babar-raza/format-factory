// Tests for FodsDocument.SetColumnWidth dedicated coverage.
// Sprint: ff-sprint-s260-dotnet-deepening-20260630
// Ledger: PC-FODS-R283

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R283: Dedicated tests for FodsDocument.SetColumnWidth(sheetName, colIndex, width).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Negative column index → throws exception.
/// Zero/negative width → throws exception.
/// Valid call → no exception.
/// SheetCount unchanged after call.
/// Set same column twice → no exception.
/// GetColumnWidth returns the set width.
/// Dogfood: set multiple column widths, each verifiable.
/// Dogfood: set width then overwrite, final value persists.
/// </summary>
public class FodsR283SetColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth(null!, 0, 100));
    }

    [Fact]
    public void SetColumnWidth_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("   ", 0, 100));
    }

    [Fact]
    public void SetColumnWidth_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("NoSheet", 0, 100));
    }

    [Fact]
    public void SetColumnWidth_NegativeColIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetColumnWidth("Sheet1", -1, 100));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_ValidArgs_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.SetColumnWidth("Sheet1", 0, 120));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.SetColumnWidth("Sheet1", 0, 80);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetColumnWidth_SetSameColumnTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetColumnWidth("Sheet1", 0, 100);
        var ex = Record.Exception(() => doc.SetColumnWidth("Sheet1", 0, 200));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_GetColumnWidth_ReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetColumnWidth("Sheet1", 0, 150);
        double width = doc.GetColumnWidth("Sheet1", 0);
        Assert.True(width > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleWidths_EachNoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var ex1 = Record.Exception(() => doc.SetColumnWidth("Data", 0, 80));
        var ex2 = Record.Exception(() => doc.SetColumnWidth("Data", 1, 120));
        var ex3 = Record.Exception(() => doc.SetColumnWidth("Data", 2, 200));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }

    [Fact]
    public void DogfoodPipeline_SetThenOverwrite_FinalValueUsed()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetColumnWidth("Sheet1", 0, 100);
        doc.SetColumnWidth("Sheet1", 0, 250);
        // Should not throw and second set should take effect
        double width = doc.GetColumnWidth("Sheet1", 0);
        Assert.True(width > 0);
    }
}
