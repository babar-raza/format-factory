// Tests for FodsDocument.GetRowHeight dedicated coverage.
// Sprint: ff-sprint-s394-dotnet-deepening-20260701
// Ledger: PC-FODS-R443

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R443: Dedicated tests for FodsDocument.GetRowHeight().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid row returns non-negative height.
/// SheetCount unchanged after GetRowHeight.
/// Idempotent (called twice same result).
/// SetRowHeight + GetRowHeight round-trips.
/// Dogfood: default row height non-negative.
/// Dogfood: multiple rows all non-negative.
/// </summary>
public class FodsR443GetRowHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowHeight_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight(null!, 0));
    }

    [Fact]
    public void GetRowHeight_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight("   ", 0));
    }

    [Fact]
    public void GetRowHeight_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight("NoSuchSheet", 0));
    }

    [Fact]
    public void GetRowHeight_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetRowHeight(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowHeight_ValidRow_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double height = doc.GetRowHeight(sheetName, 0);
        Assert.True(height >= 0.0);
    }

    [Fact]
    public void GetRowHeight_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetRowHeight(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowHeight_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double first = doc.GetRowHeight(sheetName, 0);
        double second = doc.GetRowHeight(sheetName, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowHeight_SetHeight_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetRowHeight(sheetName, 0, 25.0);
        double height = doc.GetRowHeight(sheetName, 0);
        Assert.Equal(25.0, height, 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultRow_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        double height = doc.GetRowHeight(sheetName, 0);
        Assert.True(height >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleRows_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 5; row++)
        {
            Assert.True(doc.GetRowHeight(sheetName, row) >= 0.0);
        }
    }
}
