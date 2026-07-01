// Tests for FodsDocument.GetCellMergeSpan dedicated coverage.
// Sprint: ff-sprint-s426-dotnet-deepening-20260701
// Ledger: PC-FODS-R475

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R475: Dedicated tests for FodsDocument.GetCellMergeSpan().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns positive value.
/// SheetCount unchanged after GetCellMergeSpan.
/// Idempotent (called twice same result).
/// Return type is int.
/// SetMergeSpan + GetCellMergeSpan round-trips.
/// Dogfood: default cell merge span positive.
/// Dogfood: multiple cells have positive merge span.
/// </summary>
public class FodsR475GetCellMergeSpanDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellMergeSpan_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeSpan(null!, 0, 0));
    }

    [Fact]
    public void GetCellMergeSpan_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeSpan("   ", 0, 0));
    }

    [Fact]
    public void GetCellMergeSpan_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeSpan("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellMergeSpan_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellMergeSpan("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellMergeSpan_ValidCell_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int span = doc.GetCellMergeSpan("Sheet1", 0, 0);
        Assert.True(span > 0);
    }

    [Fact]
    public void GetCellMergeSpan_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellMergeSpan("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellMergeSpan_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int first = doc.GetCellMergeSpan("Sheet1", 0, 0);
        int second = doc.GetCellMergeSpan("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellMergeSpan_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellMergeSpan("Sheet1", 0, 0);
        Assert.IsType<int>(result);
    }

    [Fact]
    public void GetCellMergeSpan_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellMergeSpan("Data", 0, 0, 3);
        int span = doc.GetCellMergeSpan("Data", 0, 0);
        Assert.Equal(3, span);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_MergeSpanPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        int span = doc.GetCellMergeSpan("Report", 0, 0);
        Assert.True(span > 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.True(doc.GetCellMergeSpan("Data", row, col) > 0);
            }
        }
    }
}
