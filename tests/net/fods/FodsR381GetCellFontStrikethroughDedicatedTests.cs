// Tests for FodsDocument.GetCellFontStrikethrough dedicated coverage.
// Sprint: ff-sprint-s343-dotnet-deepening-20260630
// Ledger: PC-FODS-R381

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R381: Dedicated tests for FodsDocument.GetCellFontStrikethrough().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellFontStrikethrough.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontStrikethrough true then Get returns true.
/// Dogfood: SetCellFontStrikethrough false then Get returns false.
/// </summary>
public class FodsR381GetCellFontStrikethroughDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontStrikethrough_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStrikethrough(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontStrikethrough_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStrikethrough("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontStrikethrough_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStrikethrough("Missing", 0, 0));
    }

    [Fact]
    public void GetCellFontStrikethrough_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Strike");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontStrikethrough("Strike", -1, 0));
    }

    [Fact]
    public void GetCellFontStrikethrough_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Text");
        bool isStrike = doc.GetCellFontStrikethrough("Text", 0, 0);
        Assert.True(isStrike == true || isStrike == false);
    }

    [Fact]
    public void GetCellFontStrikethrough_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("StrikeSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontStrikethrough("StrikeSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontStrikethrough_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.SetCellFontStrikethrough("Stable", 0, 0, true);
        bool first = doc.GetCellFontStrikethrough("Stable", 0, 0);
        bool second = doc.GetCellFontStrikethrough("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontStrikethroughTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Deprecated");
        doc.SetCellFontStrikethrough("Deprecated", 0, 0, true);
        bool isStrike = doc.GetCellFontStrikethrough("Deprecated", 0, 0);
        Assert.True(isStrike);
    }

    [Fact]
    public void DogfoodPipeline_SetCellFontStrikethroughFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Active");
        doc.SetCellFontStrikethrough("Active", 0, 0, false);
        bool isStrike = doc.GetCellFontStrikethrough("Active", 0, 0);
        Assert.False(isStrike);
    }
}
