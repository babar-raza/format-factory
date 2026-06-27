// Tests for FodsDocument.GetCellStrikethrough dedicated coverage.
// Sprint: ff-sprint-s366-dotnet-deepening-20260630
// Ledger: PC-FODS-R408

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R408: Dedicated tests for FodsDocument.GetCellStrikethrough().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns a bool (does not throw).
/// SheetCount unchanged after GetCellStrikethrough.
/// Idempotent (called twice same result).
/// Dogfood: SetCellStrikethrough true then GetCellStrikethrough returns true.
/// Dogfood: SetCellStrikethrough false then GetCellStrikethrough returns false.
/// </summary>
public class FodsR408GetCellStrikethroughDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStrikethrough_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough(null!, 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough("   ", 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellStrikethrough_NegativeRowIndex_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Strike");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStrikethrough("Strike", -1, 0));
    }

    [Fact]
    public void GetCellStrikethrough_ValidCell_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        bool st = doc.GetCellStrikethrough("Data", 0, 0);
        Assert.True(st == true || st == false);
    }

    [Fact]
    public void GetCellStrikethrough_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Style");
        int before = doc.SheetCount;
        _ = doc.GetCellStrikethrough("Style", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellStrikethrough_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetCellStrikethrough("Stable", 0, 0);
        bool second = doc.GetCellStrikethrough("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetStrikethroughTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Deprecated");
        doc.SetCellStrikethrough("Deprecated", 0, 0, true);
        bool st = doc.GetCellStrikethrough("Deprecated", 0, 0);
        Assert.True(st);
    }

    [Fact]
    public void DogfoodPipeline_SetStrikethroughFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Active");
        doc.SetCellStrikethrough("Active", 0, 0, false);
        bool st = doc.GetCellStrikethrough("Active", 0, 0);
        Assert.False(st);
    }
}
