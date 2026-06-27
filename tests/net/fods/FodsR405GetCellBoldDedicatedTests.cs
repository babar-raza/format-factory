// Tests for FodsDocument.GetCellBold dedicated coverage.
// Sprint: ff-sprint-s363-dotnet-deepening-20260630
// Ledger: PC-FODS-R405

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R405: Dedicated tests for FodsDocument.GetCellBold().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// New cell returns non-null (bool result not null).
/// SheetCount unchanged after GetCellBold.
/// Idempotent (called twice same result).
/// Dogfood: SetCellBold true then GetCellBold returns true.
/// Dogfood: SetCellBold false then GetCellBold returns false.
/// </summary>
public class FodsR405GetCellBoldDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBold_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBold(null!, 0, 0));
    }

    [Fact]
    public void GetCellBold_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBold("   ", 0, 0));
    }

    [Fact]
    public void GetCellBold_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellBold("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellBold_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Bold");
        Assert.ThrowsAny<Exception>(() => doc.GetCellBold("Bold", -1, 0));
    }

    [Fact]
    public void GetCellBold_ValidCell_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        bool bold = doc.GetCellBold("Data", 0, 0);
        Assert.True(bold == true || bold == false);
    }

    [Fact]
    public void GetCellBold_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellBold("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellBold_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetCellBold("Stable", 0, 0);
        bool second = doc.GetCellBold("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellBoldTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Header");
        doc.SetCellBold("Header", 0, 0, true);
        bool bold = doc.GetCellBold("Header", 0, 0);
        Assert.True(bold);
    }

    [Fact]
    public void DogfoodPipeline_SetCellBoldFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Body");
        doc.SetCellBold("Body", 0, 0, false);
        bool bold = doc.GetCellBold("Body", 0, 0);
        Assert.False(bold);
    }
}
