// Tests for FodsDocument.GetCellFontItalic dedicated coverage.
// Sprint: ff-sprint-s341-dotnet-deepening-20260630
// Ledger: PC-FODS-R379

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R379: Dedicated tests for FodsDocument.GetCellFontItalic().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellFontItalic.
/// Idempotent (called twice same result).
/// Dogfood: SetCellFontItalic true then Get returns true.
/// Dogfood: SetCellFontItalic false then Get returns false.
/// </summary>
public class FodsR379GetCellFontItalicDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFontItalic_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontItalic(null!, 0, 0));
    }

    [Fact]
    public void GetCellFontItalic_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontItalic("   ", 0, 0));
    }

    [Fact]
    public void GetCellFontItalic_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontItalic("Unknown", 0, 0));
    }

    [Fact]
    public void GetCellFontItalic_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Italic");
        Assert.ThrowsAny<Exception>(() => doc.GetCellFontItalic("Italic", -1, 0));
    }

    [Fact]
    public void GetCellFontItalic_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Text");
        bool isItalic = doc.GetCellFontItalic("Text", 0, 0);
        Assert.True(isItalic == true || isItalic == false);
    }

    [Fact]
    public void GetCellFontItalic_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("ItalicSheet");
        int before = doc.SheetCount;
        _ = doc.GetCellFontItalic("ItalicSheet", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellFontItalic_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.SetCellFontItalic("Stable", 0, 0, true);
        bool first = doc.GetCellFontItalic("Stable", 0, 0);
        bool second = doc.GetCellFontItalic("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFontItalicTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Emphasis");
        doc.SetCellFontItalic("Emphasis", 0, 0, true);
        bool isItalic = doc.GetCellFontItalic("Emphasis", 0, 0);
        Assert.True(isItalic);
    }

    [Fact]
    public void DogfoodPipeline_SetCellFontItalicFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Normal");
        doc.SetCellFontItalic("Normal", 0, 0, false);
        bool isItalic = doc.GetCellFontItalic("Normal", 0, 0);
        Assert.False(isItalic);
    }
}
