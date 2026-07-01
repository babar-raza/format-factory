// Tests for FodsDocument.GetCellRowHeight dedicated coverage.
// Sprint: ff-sprint-s425-dotnet-deepening-20260701
// Ledger: PC-FODS-R474

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R474: Dedicated tests for FodsDocument.GetCellRowHeight().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid row returns positive value.
/// SheetCount unchanged after GetCellRowHeight.
/// Idempotent (called twice same result).
/// Return type is double.
/// SetRowHeight + GetCellRowHeight round-trips.
/// Dogfood: default row height positive.
/// Dogfood: multiple rows have positive height.
/// </summary>
public class FodsR474GetCellRowHeightDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRowHeight_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellRowHeight(null!, 0));
    }

    [Fact]
    public void GetCellRowHeight_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellRowHeight("   ", 0));
    }

    [Fact]
    public void GetCellRowHeight_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellRowHeight("NoSuchSheet", 0));
    }

    [Fact]
    public void GetCellRowHeight_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellRowHeight("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRowHeight_ValidRow_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double height = doc.GetCellRowHeight("Sheet1", 0);
        Assert.True(height > 0);
    }

    [Fact]
    public void GetCellRowHeight_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellRowHeight("Sheet1", 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellRowHeight_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double first = doc.GetCellRowHeight("Sheet1", 0);
        double second = doc.GetCellRowHeight("Sheet1", 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellRowHeight_IsDouble()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellRowHeight("Sheet1", 0);
        Assert.IsType<double>(result);
    }

    [Fact]
    public void GetCellRowHeight_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetRowHeight("Data", 0, 25.0);
        double height = doc.GetCellRowHeight("Data", 0);
        Assert.Equal(25.0, height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultRow_HeightPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        double height = doc.GetCellRowHeight("Report", 0);
        Assert.True(height > 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleRows_AllPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int row = 0; row < 5; row++)
        {
            Assert.True(doc.GetCellRowHeight("Data", row) > 0);
        }
    }
}
