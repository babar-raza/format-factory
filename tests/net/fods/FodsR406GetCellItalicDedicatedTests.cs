// Tests for FodsDocument.GetCellItalic dedicated coverage.
// Sprint: ff-sprint-s364-dotnet-deepening-20260630
// Ledger: PC-FODS-R406

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R406: Dedicated tests for FodsDocument.GetCellItalic().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns a bool (does not throw).
/// SheetCount unchanged after GetCellItalic.
/// Idempotent (called twice same result).
/// Dogfood: SetCellItalic true then GetCellItalic returns true.
/// Dogfood: SetCellItalic false then GetCellItalic returns false.
/// </summary>
public class FodsR406GetCellItalicDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellItalic_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellItalic(null!, 0, 0));
    }

    [Fact]
    public void GetCellItalic_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellItalic("   ", 0, 0));
    }

    [Fact]
    public void GetCellItalic_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellItalic("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellItalic_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Italic");
        Assert.ThrowsAny<Exception>(() => doc.GetCellItalic("Italic", -1, 0));
    }

    [Fact]
    public void GetCellItalic_ValidCell_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        bool italic = doc.GetCellItalic("Data", 0, 0);
        Assert.True(italic == true || italic == false);
    }

    [Fact]
    public void GetCellItalic_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellItalic("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellItalic_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetCellItalic("Stable", 0, 0);
        bool second = doc.GetCellItalic("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellItalicTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Emphasis");
        doc.SetCellItalic("Emphasis", 0, 0, true);
        bool italic = doc.GetCellItalic("Emphasis", 0, 0);
        Assert.True(italic);
    }

    [Fact]
    public void DogfoodPipeline_SetCellItalicFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Normal");
        doc.SetCellItalic("Normal", 0, 0, false);
        bool italic = doc.GetCellItalic("Normal", 0, 0);
        Assert.False(italic);
    }
}
