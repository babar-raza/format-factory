// Tests for FodsDocument.GetCellVerticalAlign dedicated coverage.
// Sprint: ff-sprint-s352-dotnet-deepening-20260630
// Ledger: PC-FODS-R390

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R390: Dedicated tests for FodsDocument.GetCellVerticalAlign().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellVerticalAlign.
/// Idempotent (called twice same result).
/// Dogfood: SetCellVerticalAlign("top") then Get returns "top".
/// Dogfood: multiple cells with bottom/middle/top alignment each non-null.
/// </summary>
public class FodsR390GetCellVerticalAlignDedicatedTests
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
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign("  ", 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign("NoSheet", 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Aligned");
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlign("Aligned", -1, 0));
    }

    [Fact]
    public void GetCellVerticalAlign_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? align = doc.GetCellVerticalAlign("Data", 0, 0);
        Assert.NotNull(align);
    }

    [Fact]
    public void GetCellVerticalAlign_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Vert");
        int before = doc.SheetCount;
        _ = doc.GetCellVerticalAlign("Vert", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellVerticalAlign_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellVerticalAlign("Stable", 0, 0);
        string? second = doc.GetCellVerticalAlign("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetVerticalAlignTop_ReturnsTop()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        doc.SetCellVerticalAlign("Layout", 0, 0, "top");
        string? align = doc.GetCellVerticalAlign("Layout", 0, 0);
        Assert.NotNull(align);
        Assert.Equal("top", align);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DifferentVerticalAlignments()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellVerticalAlign("Grid", 0, 0, "top");
        doc.SetCellVerticalAlign("Grid", 1, 0, "middle");
        doc.SetCellVerticalAlign("Grid", 2, 0, "bottom");
        Assert.NotNull(doc.GetCellVerticalAlign("Grid", 0, 0));
        Assert.NotNull(doc.GetCellVerticalAlign("Grid", 1, 0));
        Assert.NotNull(doc.GetCellVerticalAlign("Grid", 2, 0));
    }
}
