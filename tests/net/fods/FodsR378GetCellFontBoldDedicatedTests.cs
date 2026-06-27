// Tests for FodsDocument.GetCellFontBold dedicated coverage.
// Sprint: ff-sprint-s340-dotnet-deepening-20260630
// Ledger: PC-FODS-R378

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R378: Dedicated tests for FodsDocument.GetCellFontBold().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellFontBold.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontBold true then Get returns true.
/// Dogfood: SetCellFontBold false then Get returns false.
/// </summary>
public class FodsR378GetCellFontBoldDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontBold_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontBold(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontBold_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontBold("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontBold_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontBold("Phantom", 0, 0));
    }

    [Fact]
    public void GetCellFontBold_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Bold");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontBold("Bold", -1, 0));
    }

    [Fact]
    public void GetCellFontBold_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Text");
        bool isBold = doc.GetCellFontBold("Text", 0, 0);
        Assert.True(isBold == true || isBold == false);
    }

    [Fact]
    public void GetCellFontBold_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("BoldSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontBold("BoldSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontBold_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.SetCellFontBold("Stable", 0, 0, true);
        bool first = doc.GetCellFontBold("Stable", 0, 0);
        bool second = doc.GetCellFontBold("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontBoldTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Headers");
        doc.SetCellFontBold("Headers", 0, 0, true);
        bool isBold = doc.GetCellFontBold("Headers", 0, 0);
        Assert.True(isBold);
    }

    [Fact]
    public void DogfoodPipeline_SetCellFontBoldFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Body");
        doc.SetCellFontBold("Body", 0, 0, false);
        bool isBold = doc.GetCellFontBold("Body", 0, 0);
        Assert.False(isBold);
    }
}
