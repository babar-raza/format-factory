// Tests for FodsDocument.GetCellTextWrap dedicated coverage.
// Sprint: ff-sprint-s367-dotnet-deepening-20260630
// Ledger: PC-FODS-R409

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R409: Dedicated tests for FodsDocument.GetCellTextWrap().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns a bool (does not throw).
/// SheetCount unchanged after GetCellTextWrap.
/// Idempotent (called twice same result).
/// Dogfood: SetCellTextWrap true then GetCellTextWrap returns true.
/// Dogfood: SetCellTextWrap false then GetCellTextWrap returns false.
/// </summary>
public class FodsR409GetCellTextWrapDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTextWrap_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextWrap(null!, 0, 0));
    }

    [Fact]
    public void GetCellTextWrap_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextWrap("   ", 0, 0));
    }

    [Fact]
    public void GetCellTextWrap_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextWrap("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellTextWrap_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Wrap");
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextWrap("Wrap", -1, 0));
    }

    [Fact]
    public void GetCellTextWrap_ValidCell_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        bool wrap = doc.GetCellTextWrap("Data", 0, 0);
        Assert.True(wrap == true || wrap == false);
    }

    [Fact]
    public void GetCellTextWrap_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Layout");
        int before = doc.SheetCount;
        _ = doc.GetCellTextWrap("Layout", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellTextWrap_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetCellTextWrap("Stable", 0, 0);
        bool second = doc.GetCellTextWrap("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetTextWrapTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        doc.SetCellTextWrap("Notes", 0, 0, true);
        bool wrap = doc.GetCellTextWrap("Notes", 0, 0);
        Assert.True(wrap);
    }

    [Fact]
    public void DogfoodPipeline_SetTextWrapFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Compact");
        doc.SetCellTextWrap("Compact", 0, 0, false);
        bool wrap = doc.GetCellTextWrap("Compact", 0, 0);
        Assert.False(wrap);
    }
}
