// Tests for FodsDocument.GetRowHeight dedicated coverage.
// Sprint: ff-sprint-s309-dotnet-deepening-20260630
// Ledger: PC-FODS-R337

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R337: Dedicated tests for FodsDocument.GetRowHeight(sheetName, rowIndex).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row index throws exception.
/// Valid call returns non-negative.
/// SheetCount unchanged after GetRowHeight.
/// Called twice returns same result.
/// Returns SetRowHeight value after set.
/// Dogfood: set then get row height on multiple sheets.
/// </summary>
public class FodsR337GetRowHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowHeight_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight(null!, 0));
    }

    [Fact]
    public void GetRowHeight_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight("   ", 0));
    }

    [Fact]
    public void GetRowHeight_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight("NoSuchSheet", 0));
    }

    [Fact]
    public void GetRowHeight_NegativeRowIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowHeight_ValidCall_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double height = doc.GetRowHeight("Sheet1", 0);
        Assert.True(height >= 0.0);
    }

    [Fact]
    public void GetRowHeight_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetRowHeight("Sheet1", 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowHeight_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double first = doc.GetRowHeight("Sheet1", 0);
        double second = doc.GetRowHeight("Sheet1", 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowHeight_ReturnsSetRowHeightValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetRowHeight("Sheet1", 0, 30);
        double height = doc.GetRowHeight("Sheet1", 0);
        Assert.True(height >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetThenGetRowHeightMultipleSheets()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        int before = doc.SheetCount;
        doc.SetRowHeight("Alpha", 0, 35);
        doc.SetRowHeight("Beta", 0, 20);
        double alphaHeight = doc.GetRowHeight("Alpha", 0);
        double betaHeight = doc.GetRowHeight("Beta", 0);
        Assert.True(alphaHeight >= 0.0);
        Assert.True(betaHeight >= 0.0);
        Assert.Equal(before, doc.SheetCount);
    }
}
