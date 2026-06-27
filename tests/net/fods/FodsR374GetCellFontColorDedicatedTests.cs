// Tests for FodsDocument.GetCellFontColor dedicated coverage.
// Sprint: ff-sprint-s337-dotnet-deepening-20260630
// Ledger: PC-FODS-R374

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R374: Dedicated tests for FodsDocument.GetCellFontColor().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellFontColor.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontColor then Get returns color.
/// Dogfood: Multiple cells with different font colors all non-null.
/// </summary>
public class FodsR374GetCellFontColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontColor_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("Invisible", 0, 0));
    }

    [Fact]
    public void GetCellFontColor_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Color");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontColor("Color", -1, 0));
    }

    [Fact]
    public void GetCellFontColor_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Font");
        string? fontColor = doc.GetCellFontColor("Font", 0, 0);
        Assert.NotNull(fontColor);
    }

    [Fact]
    public void GetCellFontColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("ColorSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontColor("ColorSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontColor_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Repeat");
        doc.SetCellFontColor("Repeat", 0, 0, "#CC0000");
        string? first = doc.GetCellFontColor("Repeat", 0, 0);
        string? second = doc.GetCellFontColor("Repeat", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontColorThenGet_ReturnsColor()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Highlights");
        doc.SetCellFontColor("Highlights", 0, 0, "#003366");
        string? fontColor = doc.GetCellFontColor("Highlights", 0, 0);
        Assert.NotNull(fontColor);
        Assert.Equal("#003366", fontColor);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsDifferentColors_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Palette");
        doc.SetCellFontColor("Palette", 0, 0, "#FF0000");
        doc.SetCellFontColor("Palette", 0, 1, "#00AA00");
        doc.SetCellFontColor("Palette", 0, 2, "#0000FF");
        Assert.NotNull(doc.GetCellFontColor("Palette", 0, 0));
        Assert.NotNull(doc.GetCellFontColor("Palette", 0, 1));
        Assert.NotNull(doc.GetCellFontColor("Palette", 0, 2));
    }
}
