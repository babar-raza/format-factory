// Tests for FodsDocument.GetCellVerticalAlign dedicated coverage.
// Sprint: ff-sprint-s379-dotnet-deepening-20260630
// Ledger: PC-FODS-R422

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R422: Dedicated tests for FodsDocument.GetCellVerticalAlign().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellVerticalAlign.
/// Idempotent (called twice same result).
/// Dogfood: SetVerticalAlign middle+Get.
/// Dogfood: multiple cells top/middle/bottom.
/// </summary>
public class FodsR422GetCellVerticalAlignDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellVerticalAlign_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign(null!, 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign("   ", 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign("Missing", 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign("Data", -1, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        string align = doc.GetCellVerticalAlign("Layout", 0, 0);
        Assert.NotNull(align);
    }

    [Fact]
    public void GetCellVerticalAlign_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetCellVerticalAlign("Data", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellVerticalAlign_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string first = doc.GetCellVerticalAlign("Stable", 0, 0);
        string second = doc.GetCellVerticalAlign("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetVerticalAlignMiddleThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellVerticalAlign("Report", 0, 0, "middle");
        string align = doc.GetCellVerticalAlign("Report", 0, 0);
        Assert.Equal("middle", align);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DistinctAlignments()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellVerticalAlign("Grid", 0, 0, "top");
        doc.SetCellVerticalAlign("Grid", 1, 0, "middle");
        doc.SetCellVerticalAlign("Grid", 2, 0, "bottom");
        Assert.Equal("top", doc.GetCellVerticalAlign("Grid", 0, 0));
        Assert.Equal("middle", doc.GetCellVerticalAlign("Grid", 1, 0));
        Assert.Equal("bottom", doc.GetCellVerticalAlign("Grid", 2, 0));
    }
}
