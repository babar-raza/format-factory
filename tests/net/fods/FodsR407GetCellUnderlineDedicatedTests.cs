// Tests for FodsDocument.GetCellUnderline dedicated coverage.
// Sprint: ff-sprint-s365-dotnet-deepening-20260630
// Ledger: PC-FODS-R407

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R407: Dedicated tests for FodsDocument.GetCellUnderline().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns a bool (does not throw).
/// SheetCount unchanged after GetCellUnderline.
/// Idempotent (called twice same result).
/// Dogfood: SetCellUnderline true then GetCellUnderline returns true.
/// Dogfood: SetCellUnderline false then GetCellUnderline returns false.
/// </summary>
public class FodsR407GetCellUnderlineDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellUnderline_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline(null!, 0, 0));
    }

    [Fact]
    public void GetCellUnderline_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline("   ", 0, 0));
    }

    [Fact]
    public void GetCellUnderline_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellUnderline_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Underline");
        Assert.ThrowsAny<Exception>(() => doc.GetCellUnderline("Underline", -1, 0));
    }

    [Fact]
    public void GetCellUnderline_ValidCell_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        bool ul = doc.GetCellUnderline("Data", 0, 0);
        Assert.True(ul == true || ul == false);
    }

    [Fact]
    public void GetCellUnderline_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellUnderline("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellUnderline_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetCellUnderline("Stable", 0, 0);
        bool second = doc.GetCellUnderline("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellUnderlineTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Links");
        doc.SetCellUnderline("Links", 0, 0, true);
        bool ul = doc.GetCellUnderline("Links", 0, 0);
        Assert.True(ul);
    }

    [Fact]
    public void DogfoodPipeline_SetCellUnderlineFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Plain");
        doc.SetCellUnderline("Plain", 0, 0, false);
        bool ul = doc.GetCellUnderline("Plain", 0, 0);
        Assert.False(ul);
    }
}
