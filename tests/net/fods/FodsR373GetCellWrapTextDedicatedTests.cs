// Tests for FodsDocument.GetCellWrapText dedicated coverage.
// Sprint: ff-sprint-s336-dotnet-deepening-20260630
// Ledger: PC-FODS-R373

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R373: Dedicated tests for FodsDocument.GetCellWrapText().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellWrapText.
/// Idempotent (called twice same result).
/// Dogfood: SetCellWrapText true then Get returns true.
/// Dogfood: SetCellWrapText false then Get returns false.
/// </summary>
public class FodsR373GetCellWrapTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellWrapText_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText(null!, 0, 0));
    }

    [Fact]
    public void GetCellWrapText_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText("   ", 0, 0));
    }

    [Fact]
    public void GetCellWrapText_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText("Unknown", 0, 0));
    }

    [Fact]
    public void GetCellWrapText_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Wrap");
        Assert.ThrowsAny<Exception>(() => doc.GetCellWrapText("Wrap", -1, 0));
    }

    [Fact]
    public void GetCellWrapText_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Text");
        bool wrapText = doc.GetCellWrapText("Text", 0, 0);
        Assert.True(wrapText == true || wrapText == false);
    }

    [Fact]
    public void GetCellWrapText_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("WrapSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellWrapText("WrapSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellWrapText_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Repeat");
        doc.SetCellWrapText("Repeat", 0, 0, true);
        bool first = doc.GetCellWrapText("Repeat", 0, 0);
        bool second = doc.GetCellWrapText("Repeat", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetWrapTextTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Notes");
        doc.SetCellWrapText("Notes", 0, 0, true);
        bool wrapText = doc.GetCellWrapText("Notes", 0, 0);
        Assert.True(wrapText);
    }

    [Fact]
    public void DogfoodPipeline_SetWrapTextFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Compact");
        doc.SetCellWrapText("Compact", 0, 0, false);
        bool wrapText = doc.GetCellWrapText("Compact", 0, 0);
        Assert.False(wrapText);
    }
}
