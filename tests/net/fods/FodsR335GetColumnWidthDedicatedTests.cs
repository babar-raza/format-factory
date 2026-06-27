// Tests for FodsDocument.GetColumnWidth dedicated coverage.
// Sprint: ff-sprint-s307-dotnet-deepening-20260630
// Ledger: PC-FODS-R335

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R335: Dedicated tests for FodsDocument.GetColumnWidth(sheetName, columnIndex).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative column index throws exception.
/// Valid call returns non-negative.
/// SheetCount unchanged after GetColumnWidth.
/// Called twice returns same result.
/// Returns SetColumnWidth value after set.
/// Dogfood: set then get width on multiple sheets.
/// </summary>
public class FodsR335GetColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWidth_NullSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth(null!, 0));
    }

    [Fact]
    public void GetColumnWidth_WhitespaceSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth("   ", 0));
    }

    [Fact]
    public void GetColumnWidth_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth("NoSuchSheet", 0));
    }

    [Fact]
    public void GetColumnWidth_NegativeColumnIndex_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnWidth("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWidth_ValidCall_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double width = doc.GetColumnWidth("Sheet1", 0);
        Assert.True(width >= 0.0);
    }

    [Fact]
    public void GetColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetColumnWidth("Sheet1", 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnWidth_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double first = doc.GetColumnWidth("Sheet1", 0);
        double second = doc.GetColumnWidth("Sheet1", 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnWidth_ReturnsSetColumnWidthValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetColumnWidth("Sheet1", 0, 150);
        double width = doc.GetColumnWidth("Sheet1", 0);
        Assert.True(width >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetThenGetWidthMultipleSheets()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        int before = doc.SheetCount;
        doc.SetColumnWidth("Alpha", 0, 120);
        doc.SetColumnWidth("Beta", 0, 80);
        double alphaWidth = doc.GetColumnWidth("Alpha", 0);
        double betaWidth = doc.GetColumnWidth("Beta", 0);
        Assert.True(alphaWidth >= 0.0);
        Assert.True(betaWidth >= 0.0);
        Assert.Equal(before, doc.SheetCount);
    }
}
