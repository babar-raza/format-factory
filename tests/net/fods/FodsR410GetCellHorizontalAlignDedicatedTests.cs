// Tests for FodsDocument.GetCellHorizontalAlign dedicated coverage.
// Sprint: ff-sprint-s368-dotnet-deepening-20260630
// Ledger: PC-FODS-R410

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R410: Dedicated tests for FodsDocument.GetCellHorizontalAlign().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellHorizontalAlign.
/// Idempotent (called twice same result).
/// Dogfood: SetCellHorizontalAlign "center" then Get returns "center".
/// Dogfood: multiple cells left/center/right each non-null.
/// </summary>
public class FodsR410GetCellHorizontalAlignDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellHorizontalAlign_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlign(null!, 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlign_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlign("   ", 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlign_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlign("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellHorizontalAlign_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Align");
        Assert.ThrowsAny<Exception>(() => doc.GetCellHorizontalAlign("Align", -1, 0));
    }

    [Fact]
    public void GetCellHorizontalAlign_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        string? align = doc.GetCellHorizontalAlign("Data", 0, 0);
        Assert.NotNull(align);
    }

    [Fact]
    public void GetCellHorizontalAlign_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        int before = doc.SheetCount;
        _ = doc.GetCellHorizontalAlign("Layout", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellHorizontalAlign_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetCellHorizontalAlign("Stable", 0, 0);
        string? second = doc.GetCellHorizontalAlign("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAlignCenter_ReturnsCenter()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Header");
        doc.SetCellHorizontalAlign("Header", 0, 0, "center");
        string? align = doc.GetCellHorizontalAlign("Header", 0, 0);
        Assert.NotNull(align);
        Assert.Equal("center", align);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_EachNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.SetCellHorizontalAlign("Grid", 0, 0, "left");
        doc.SetCellHorizontalAlign("Grid", 1, 0, "center");
        doc.SetCellHorizontalAlign("Grid", 2, 0, "right");
        Assert.NotNull(doc.GetCellHorizontalAlign("Grid", 0, 0));
        Assert.NotNull(doc.GetCellHorizontalAlign("Grid", 1, 0));
        Assert.NotNull(doc.GetCellHorizontalAlign("Grid", 2, 0));
    }
}
