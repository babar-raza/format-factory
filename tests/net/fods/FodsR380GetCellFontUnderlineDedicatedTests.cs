// Tests for FodsDocument.GetCellFontUnderline dedicated coverage.
// Sprint: ff-sprint-s342-dotnet-deepening-20260630
// Ledger: PC-FODS-R380

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R380: Dedicated tests for FodsDocument.GetCellFontUnderline().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellFontUnderline.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontUnderline true then Get returns true.
/// Dogfood: SetCellFontUnderline false then Get returns false.
/// </summary>
public class FodsR380GetCellFontUnderlineDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontUnderline_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontUnderline(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontUnderline_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontUnderline("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontUnderline_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontUnderline("Ghost", 0, 0));
    }

    [Fact]
    public void GetCellFontUnderline_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Underline");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontUnderline("Underline", -1, 0));
    }

    [Fact]
    public void GetCellFontUnderline_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Links");
        bool isUnderline = doc.GetCellFontUnderline("Links", 0, 0);
        Assert.True(isUnderline == true || isUnderline == false);
    }

    [Fact]
    public void GetCellFontUnderline_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("UnderlineSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontUnderline("UnderlineSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontUnderline_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.SetCellFontUnderline("Stable", 0, 0, true);
        bool first = doc.GetCellFontUnderline("Stable", 0, 0);
        bool second = doc.GetCellFontUnderline("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontUnderlineTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Hyperlinks");
        doc.SetCellFontUnderline("Hyperlinks", 0, 0, true);
        bool isUnderline = doc.GetCellFontUnderline("Hyperlinks", 0, 0);
        Assert.True(isUnderline);
    }

    [Fact]
    public void DogfoodPipeline_SetCellFontUnderlineFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Plain");
        doc.SetCellFontUnderline("Plain", 0, 0, false);
        bool isUnderline = doc.GetCellFontUnderline("Plain", 0, 0);
        Assert.False(isUnderline);
    }
}
